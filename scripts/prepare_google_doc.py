"""Prepare portable source blocks and exact UTF-16 formatting for a native Doc."""
import argparse
import hashlib
import json
from pathlib import Path
import re


def units(text):
    return len(text.encode('utf-16-le')) // 2


def inline(source):
    pieces, styles, offset, cursor = [], [], 0, 0
    pattern = r'\*\*([^*]+)\*\*|`([^`]+)`|\[([^\]]+)\]\(([^)]+)\)'
    for match in re.finditer(pattern, source):
        before = source[cursor:match.start()]
        pieces.append(before); offset += units(before)
        if match[1] is not None:
            value, style = match[1], {'bold': True}
        elif match[2] is not None:
            value, style = match[2], {'weightedFontFamily': {'fontFamily':'Courier New'}, 'fontSize': {'magnitude':9,'unit':'PT'}}
        else:
            value, style = match[3], {'link': {'url':match[4]}}
        pieces.append(value)
        styles.append({'start':offset,'end':offset+units(value),'style':style})
        offset += units(value); cursor = match.end()
    pieces.append(source[cursor:])
    return ''.join(pieces), styles


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--source',type=Path,default=Path('report/final-report.md'))
    parser.add_argument('--output',type=Path,default=Path('report/google-doc-source.json'))
    args=parser.parse_args()
    lines=args.source.read_text().splitlines()
    blocks=[]; tables=[]; images=[]; code=False; index=0; first=True
    while index<len(lines):
        line=lines[index].strip()
        if not line or line=='<!-- page -->':index+=1;continue
        kind='body'; raw=line
        if line.startswith('```'):
            code=not code;index+=1;continue
        if code:kind='code';raw=lines[index]
        elif line.startswith('|'):
            rows=[]
            while index<len(lines) and lines[index].startswith('|'):
                row=[s.strip() for s in lines[index].strip().strip('|').split('|')]
                if not all(re.fullmatch(r'[-: ]+',s) for s in row):rows.append(row)
                index+=1
            raw=f'[TABLE_{len(tables)}]';tables.append({'marker':raw,'rows':rows});kind='table';index-=1
        elif line.startswith('!['):
            match=re.fullmatch(r'!\[([^\]]*)\]\(([^)]+)\)',line)
            raw=f'[FIGURE_{len(images)}]';images.append({'marker':raw,'alt':match[1],'path':str(args.source.parent/match[2])});kind='image'
        elif line.startswith('# '):
            raw=line[2:];kind='title' if first else 'h1';first=False
        elif line.startswith('## '):
            raw=line[3:];kind='subtitle' if raw.startswith('Metamorphic validation') else ('h1' if raw.startswith('1. ') else 'h2')
        text,styles=inline(raw)
        blocks.append({'kind':kind,'text':text,'styles':styles})
        index+=1
    text='';position=1
    for block in blocks:
        block['start']=position;block['end']=position+units(block['text'])
        text+=block['text']+'\n';position=block['end']+1
    tab='t.0'
    requests=[{'insertText':{'location':{'index':1,'tabId':tab},'text':text}},
      {'updateParagraphStyle':{'range':{'startIndex':1,'endIndex':position,'tabId':tab},'paragraphStyle':{'namedStyleType':'NORMAL_TEXT','alignment':'JUSTIFIED','lineSpacing':110,'spaceAbove':{'magnitude':0,'unit':'PT'},'spaceBelow':{'magnitude':6,'unit':'PT'}},'fields':'namedStyleType,alignment,lineSpacing,spaceAbove,spaceBelow'}},
      {'updateTextStyle':{'range':{'startIndex':1,'endIndex':position-1,'tabId':tab},'textStyle':{'weightedFontFamily':{'fontFamily':'EB Garamond'},'fontSize':{'magnitude':11,'unit':'PT'}},'fields':'weightedFontFamily,fontSize'}}]
    for block in blocks:
        start,end=block['start'],block['end']
        span={'startIndex':start,'endIndex':end,'tabId':tab}
        if block['kind'] in ['title','subtitle','h1','h2']:
            named,size={'title':('TITLE',30),'subtitle':('SUBTITLE',16),'h1':('HEADING_1',20),'h2':('HEADING_2',16)}[block['kind']]
            props={'namedStyleType':named,'keepWithNext':True}
            if block['kind'] in ['title','subtitle']:props['alignment']='CENTER'
            requests+=[{'updateParagraphStyle':{'range':span,'paragraphStyle':props,'fields':','.join(props)}},{'updateTextStyle':{'range':span,'textStyle':{'fontSize':{'magnitude':size,'unit':'PT'}},'fields':'fontSize'}}]
        if block['kind']=='code':
            requests.append({'updateTextStyle':{'range':span,'textStyle':{'weightedFontFamily':{'fontFamily':'Courier New'},'fontSize':{'magnitude':9,'unit':'PT'}},'fields':'weightedFontFamily,fontSize'}})
        for style in block['styles']:
            requests.append({'updateTextStyle':{'range':{'startIndex':start+style['start'],'endIndex':start+style['end'],'tabId':tab},'textStyle':style['style'],'fields':','.join(style['style'])}})
    result={'schema':'agentqa.google-doc-source.v1','source_sha256':hashlib.sha256(args.source.read_bytes()).hexdigest(),'text':text,'blocks':blocks,'tables':tables,'images':images,'initial_requests':requests,'style_reference':'Neuroevolution report: EB Garamond 11, justified 110 percent lines, native headings/tables/figures','final_pdf':False}
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print({'blocks':len(blocks),'tables':len(tables),'images':len(images),'utf16_units':position-1,'requests':len(requests)})

if __name__=='__main__':main()
