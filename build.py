#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Zero-dependency static website builder. Edit site.json, run python3 build.py."""
import json, shutil, html
from pathlib import Path
from urllib.parse import urlparse
ROOT=Path(__file__).resolve().parent
C=json.loads((ROOT/'site.json').read_text())
esc=html.escape
name=C['name']; short=C['short']; phone=C['phone']; theme=C['theme']; domain=C.get('domain','').rstrip('/')
if domain and (urlparse(domain).scheme not in ('http','https') or not urlparse(domain).netloc):
    raise SystemExit('domain 必须是完整的 https:// 域名')
OUT=ROOT/'dist'; OUT.mkdir(exist_ok=True)
for stale in list(OUT.glob('news-*.html'))+list(OUT.glob('case-*.html')): stale.unlink()
shutil.copytree(ROOT/'assets',OUT/'assets',dirs_exist_ok=True,ignore=shutil.ignore_patterns('*-original.png'))
for f in ('site.css','site.js'): shutil.copy(ROOT/f,OUT/f)
nav=[('services.html','服务项目'),('news.html','新闻资讯'),('cases.html','案例'),('pricing.html','费用说明'),('guide.html','搬家指南'),('about.html','关于我们')]
content_file=ROOT/'content.json'
items=json.loads(content_file.read_text(encoding='utf-8')) if content_file.exists() else []
published=[x for x in items if x.get('status')=='published' and x.get('kind') in ('news','case')]
published.sort(key=lambda x:x.get('published_at',''), reverse=True)
brands={'zhong':('ZHONGAN MOVING','珍贵如初，<br><em>安稳抵达新家。</em>','从物品清单到新家落位，把搬家的细节逐项理清。让新生活，从一次从容的搬迁开始。','安心，在细节里','RESIDENTIAL MOVING · GUANGZHOU'), 'you':('YOUBANG MOVING','下一站，新家。<br><em>一起轻松出发。</em>','纸箱装下生活，新的日常正在路上。把你的搬家计划告诉友帮，从整理需求开始，少一点忙乱。','新生活，正在打包中','A FRESH START · GUANGZHOU'), 'sheng':('SHENGYUAN MOVING','迁新址，<br><em>让计划有序落地。</em>','梳理物品、协调时间、确认现场条件。让每一步搬迁安排，都有清晰的起点与交接。','有计划，也有条理','MOVE WITH A PLAN · GUANGZHOU')}
english,headline,intro,label,tag=brands[theme]
services=[('home','居民搬家','从旧家到新家，照顾生活的细节。','适合整户搬迁、租房换房等需求。咨询时说明物品数量、两端楼层、电梯及停车条件，便于核实车辆与人工安排。'),('small','小件搬运','轻装出发，也值得认真安排。','适合纸箱、行李、小型家具等少量物品。建议提供尺寸、数量和现场照片，避免仅凭“一点东西”估算运力。'),('office','办公室搬迁','把新的工作日，安排得更从容。','办公桌椅、设备、档案需要分组清点。咨询时说明工位数量、拆装需求、物业放行要求和可施工时间。')]
if theme=='sheng': services=[services[2],services[0],services[1]]
faqs=[('广州搬家费用主要由哪些因素决定？','费用通常与车辆及车次、人工、两端楼层与电梯、搬运距离、拆装打包及特殊物品有关。请提供两端地址和物品清单，并在确认服务前核对书面报价的包含项与另计项。'),('预约前需要准备哪些信息？','准备搬出与搬入区域、计划日期、物品清单、两端楼层和电梯情况。较大家具需说明尺寸，另需确认车辆能否进入小区、装卸点到电梯的距离及物业搬运时段。'),('没有电梯或者车辆无法停到楼下，怎么办？','咨询时如实说明楼层、楼梯宽度、物品尺寸和步行搬运距离。这些条件可能影响人员安排、可搬物品和费用，是否能够承接需逐项确认。'),('家具拆装、打包材料是否包含在费用里？','不要默认包含。请在报价前列出需要拆装和打包的物品，核实人工、材料、复装和额外作业是否单独计费，并保留确认记录。'),('能否预约当天搬家？','当天能否安排取决于车辆、人员、路程和现场条件。请直接拨打咨询电话核实，不要以网页浏览或需求清单生成作为预约成功的依据。'),('搬运完成后应如何验收？','按清单核对数量，检查外观、家具配件和拆装结果；如有问题，及时拍照并与现场负责人沟通，保存服务约定、报价及相关记录。')]
if theme=='you':
 faqs[1]=('租房搬家，怎样整理才能少遗漏？','按房间或用途分箱，箱外标记目的房间。证件、钥匙、充电器和当天要用的生活用品单独随身保管；退房前检查抽屉、阳台、柜顶和储物空间。')
if theme=='sheng':
 faqs[1]=('办公室搬迁怎样安排清点与交接？','建立按部门、工位编号的物品清单，将设备、配件与线缆对应标记。与物业确认搬运时间、货梯和车辆通行条件；涉及业务数据的设备应提前备份并安排专人交接。')

def faq_html(items):
 return '<div class="faq-list">'+''.join(f'<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>' for q,a in items)+'</div>'
def cards():
 return '<div class="cards">'+''.join(f'<article class="service-card"><span class="num">0{i} / {"MOVING" if k!="office" else "BUSINESS"}</span><h3>{t}</h3><p>{s}</p><a class="text-link" href="services.html#{k}">查看咨询要点 ↗</a></article>' for i,(k,t,s,d) in enumerate(services,1))+'</div>'
def cta():
 return f'<div class="wrap"><section class="cta"><div><span class="eyebrow">LET’S TALK ABOUT YOUR MOVE</span><h2>新的起点，从聊聊开始。</h2><p>说明时间、地点和物品，让沟通更具体。</p></div><a class="btn" href="tel:{phone}">电话咨询 {phone} ↗</a></section></div>'
def pagehero(title,desc):
 return f'<section class="page-hero"><div class="wrap"><nav class="breadcrumbs" aria-label="面包屑"><a href="index.html">首页</a> / {title}</nav><h1>{title}</h1><p>{desc}</p></div></section>'
def write(filename,title,desc,body,faq=None,article=False,article_data=None):
 canonical=domain+'/'+('' if filename=='index.html' else filename) if domain else ''
 org={'@type':'MovingCompany','@id':(domain+'/' if domain else '')+'#company','name':name,'telephone':'+86'+phone}
 if domain: org['url']=domain+'/'
 if C.get('address'): org['address']={'@type':'PostalAddress','streetAddress':C['address'],'addressLocality':'广州市','addressCountry':'CN'}
 graph=[org,{'@type':'WebPage','name':title,'description':desc,'inLanguage':'zh-CN','about':{'@id':org['@id']}}]
 if canonical: graph[-1]['url']=canonical
 if filename!='index.html':
  crumb={'@type':'BreadcrumbList','itemListElement':[{'@type':'ListItem','position':1,'name':'首页','item':domain+'/' if domain else 'index.html'},{'@type':'ListItem','position':2,'name':title,'item':canonical or filename}]};graph.append(crumb)
 if faq: graph.append({'@type':'FAQPage','mainEntity':[{'@type':'Question','name':q,'acceptedAnswer':{'@type':'Answer','text':a}} for q,a in faq]})
 if article:
  article_node={'@type':'Article','headline':title,'author':{'@id':org['@id']},'publisher':{'@id':org['@id']},'inLanguage':'zh-CN','mainEntityOfPage':canonical or filename}
  if article_data:
   article_node['datePublished']=article_data['published_at']
   article_node['dateModified']=article_data['updated_at']
   if article_data.get('image') and domain:article_node['image']=domain+'/'+article_data['image']
  graph.append(article_node)
 head=f'<meta name="description" content="{esc(desc,quote=True)}"><meta name="theme-color" content="#142c45"><meta property="og:locale" content="zh_CN"><meta property="og:type" content="website"><meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(desc)}"><meta property="og:site_name" content="{name}">'
 if canonical:head+=f'<link rel="canonical" href="{esc(canonical)}"><meta property="og:url" content="{esc(canonical)}">'
 links=''.join(f'<a href="{f}"'+(' aria-current="page"' if filename==f else '')+f'>{t}</a>' for f,t in nav)
 brand=f'<a class="brand" href="index.html" aria-label="{name}首页"><span class="brand-symbol" aria-hidden="true">{short[0]}</span><span><strong>{short}搬家</strong><small>{english}</small></span></a>'
 address=f'<p>{esc(C["address"])}</p>' if C.get('address') else ''
 schema_json=json.dumps({'@context':'https://schema.org','@graph':graph},ensure_ascii=False).replace('</','<\\/')
 htmltext=f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)}</title>{head}<link rel="icon" href="assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="site.css"><script type="application/ld+json">{schema_json}</script><script src="site.js" defer></script></head><body class="{theme}"><a class="skip" href="#main">跳至正文</a><div class="topline"><div class="wrap"><span>{name}</span><span>搬家之前，把每个细节说清楚。</span></div></div><header class="site-header"><div class="wrap nav-wrap">{brand}<button class="menu-btn" aria-label="切换导航菜单" aria-expanded="false" aria-controls="navigation">菜单 ☰</button><nav id="navigation" class="nav-links" aria-label="主导航">{links}<a href="contact.html" {'aria-current="page"' if filename=='contact.html' else ''}>搬家咨询 ↗</a></nav><a class="nav-phone" href="tel:{phone}"><span>直接联系</span>{phone}</a></div></header><main id="main">{body}</main><footer class="footer"><div class="wrap"><div class="footer-grid"><div>{brand}<p style="margin-top:20px">{name}<br>咨询电话：<a href="tel:{phone}">{phone}</a></p>{address}</div><div class="footer-links"><strong>了解搬家</strong><a href="services.html">服务项目</a><a href="pricing.html">费用说明</a><a href="guide.html">搬家指南</a><a href="news.html">新闻资讯</a><a href="cases.html">案例</a></div><div class="footer-links"><strong>联系与支持</strong><a href="about.html">关于{short}</a><a href="faq.html">常见问题</a><a href="contact.html">搬家咨询</a><a href="privacy.html">隐私说明</a></div></div><div class="footer-bottom"><span>© {name}</span></div></div></footer><a class="mobile-call" href="tel:{phone}"><span>联系{short} · 电话咨询</span><b>{phone} ↗</b></a></body></html>'''
 (OUT/filename).write_text(htmltext,encoding='utf-8')

def item_url(x):
 return ('news-' if x['kind']=='news' else 'case-')+x['id']+'.html'

def item_card(x):
 label='新闻资讯' if x['kind']=='news' else '搬家案例'
 cover=f'<img loading="lazy" src="{esc(x["image"],quote=True)}" alt="{esc(x.get("image_alt") or x["title"],quote=True)}" width="600" height="400">' if x.get('image') else '<div class="article-placeholder" aria-hidden="true">'+('NEWS' if x['kind']=='news' else 'CASE')+'</div>'
 return f'<article class="article-card"><a href="{item_url(x)}">{cover}<div class="article-card-body"><span class="eyebrow">{label} · {esc(x["published_at"][:10])}</span><h3>{esc(x["title"])}</h3><p>{esc(x["summary"])}</p><span class="text-link">阅读详情 ↗</span></div></a></article>'

def home_content():
 blocks=[]
 for kind,label,filename in [('news','新闻资讯','news.html'),('case','搬家案例','cases.html')]:
  subset=[x for x in published if x['kind']==kind][:2]
  if subset:blocks.append(f'<section class="section"><div class="wrap"><div class="section-head"><div><span class="eyebrow">LATEST / {kind.upper()}</span><h2>{label}</h2></div><a class="text-link" href="{filename}">查看全部 ↗</a></div><div class="article-grid">'+''.join(item_card(x) for x in subset)+'</div></div></section>')
 return ''.join(blocks)

def content_pages():
 for kind,label,filename in [('news','新闻资讯','news.html'),('case','搬家案例','cases.html')]:
  subset=[x for x in published if x['kind']==kind]
  intro='搬家准备、费用理解与服务动态。' if kind=='news' else '已发布的搬迁项目记录。案例内容以实际提供的资料为准。'
  listing='<section class="section"><div class="wrap">'+('<div class="article-grid">'+''.join(item_card(x) for x in subset)+'</div>' if subset else f'<div class="empty-content"><h2>内容整理中</h2><p>{"后续将在这里发布搬家相关资讯。" if kind=="news" else "目前尚未发布可核实的搬迁案例。"}</p><a class="text-link" href="contact.html">咨询搬家服务 ↗</a></div>')+'</div></section>'
  write(filename,f'{label}｜{name}',f'{name}{label}：{intro}',pagehero(label,intro)+listing)
 for x in published:
  label='新闻资讯' if x['kind']=='news' else '搬家案例'
  filename=item_url(x)
  photo=f'<figure class="article-feature"><img src="{esc(x["image"],quote=True)}" alt="{esc(x.get("image_alt") or x["title"],quote=True)}" width="1200" height="800"></figure>' if x.get('image') else ''
  paras=''.join('<p>'+esc(t)+'</p>' for t in x['body'].split('\n\n') if t.strip())
  body=pagehero(esc(x['title']),esc(x['summary']))+f'<article class="wrap section content"><p class="article-meta">{label} · 发布于 {esc(x["published_at"][:10])}</p>{photo}<div class="article-body">{paras}</div><div class="related"><a class="text-link" href="{"news.html" if x["kind"]=="news" else "cases.html"}">返回{label} ↗</a><a class="text-link" href="contact.html">联系咨询 ↗</a></div></article>'
  write(filename,f'{x["title"]}｜{name}',x['summary'],body,article=True,article_data=x)

hero=f'''<section class="hero"><div class="wrap"><div class="hero-grid"><div class="hero-copy"><span class="eyebrow">{tag}</span><h1>{headline}</h1><p>{intro}</p><div class="actions"><a class="btn" href="contact.html">聊聊我的搬家计划 <span>↗</span></a><a class="btn outline" href="services.html">了解服务</a></div></div><figure class="hero-visual"><picture><source srcset="assets/hero.webp" type="image/webp"><img src="assets/hero.jpg" alt="{'现代办公室内整理设备与搬迁物品的场景示意' if theme=='sheng' else '现代住宅中整理纸箱与搬运物品的场景示意'}" width="1536" height="1024" fetchpriority="high"></picture><div class="image-label"><small>A NEW CHAPTER</small><strong>{label}</strong></div><figcaption>场景示意</figcaption></figure></div><div class="hero-bottom"><div><b>需求说清楚</b>时间 / 地点 / 物品</div><div><b>费用问明白</b>包含项 / 另计项</div><div><b>交接有清单</b>核对 / 检查 / 确认</div></div></div></section>'''
steps=[('沟通需求','说明搬出搬入位置、物品数量和计划日期。'),('核实方案','核对车辆、人员、费用组成与额外作业。'),('确认安排','明确搬运时段、现场条件和双方约定。'),('逐项交接','对照清单检查物品数量、外观与摆放。')]
body=hero+f'''<section class="section"><div class="wrap"><div class="section-head"><div><span class="eyebrow">01 / EVERY MOVE IS DIFFERENT</span><h2>{'为每一种生活变动，<br>找到合适的安排。' if theme!='sheng' else '不同规模的搬迁，<br>从明确需求开始。'}</h2></div><p>从家庭物品到办公设备，按实际需求沟通。具体承接范围与时间，请电话确认。</p></div>{cards()}</div></section><section class="section band"><div class="wrap"><span class="eyebrow">02 / A CLEAR PLAN</span><h2>搬家这件事，<br>一步一步安排好。</h2><div class="steps">'''+''.join(f'<div class="step"><span class="num">0{i}</span><h3>{t}</h3><p>{d}</p></div>' for i,(t,d) in enumerate(steps,1))+'''</div></div></section><section class="section"><div class="wrap split"><div><span class="eyebrow">03 / BEFORE YOU MOVE</span><h2>费用的每一项，<br>都值得提前问清。</h2><p>搬家没有适用于所有人的统一价格。物品、楼层和搬运条件，会影响具体方案。</p><a class="text-link" href="pricing.html">了解费用组成 ↗</a></div><ul class="check-list"><li><i>01</i><div><b>车辆与人工</b><span>车型、车次、人员及等待时间如何计算？</span></div></li><li><i>02</i><div><b>楼层与距离</b><span>是否有电梯？车辆到门口有多远？</span></div></li><li><i>03</i><div><b>拆装与打包</b><span>材料、拆装、特殊物品是否单独计费？</span></div></li></ul></div></section><section class="section" style="padding-top:0"><div class="wrap"><div class="section-head"><div><span class="eyebrow">04 / GOOD TO KNOW</span><h2>搬家前，你可能想问。</h2></div><a class="text-link" href="faq.html">全部常见问题 ↗</a></div>'''+faq_html(faqs[:3])+'</div></section>'+cta()
body+=home_content()
write('index.html',f'{name}｜广州搬家咨询与搬迁指南',f'{name}网站，提供搬家服务咨询、费用因素说明和搬家准备指南。电话{phone}，具体承接范围及报价请咨询确认。',body,faqs[:3])
body=pagehero('每一种搬迁，都从需求开始。','整理物品、明确现场条件，再沟通适合你的搬家方案。以下为常见需求类型，具体服务范围以电话确认为准。')+'<div class="wrap section">'+''.join(f'<section class="split" id="{k}" style="margin-bottom:70px"><div><span class="eyebrow">0{i} / {k.upper()} MOVING</span><h2>{t}</h2><p>{s}</p><a class="btn" href="contact.html">咨询这类搬家 ↗</a></div><div class="content"><p>{d}</p><h3>咨询时说明</h3><ul><li>计划搬运日期、搬出与搬入的具体位置。</li><li>{"工位数量、设备类型、档案箱数及分批搬运要求。" if k=="office" else "家具家电清单、纸箱数量，以及大件物品的长宽高。"}</li><li>两端楼层、电梯尺寸、停车点和物业允许的搬运时段。</li><li>是否需要拆装、打包、材料或其他额外作业。</li></ul><p class="note">贵重物品、精密设备或需专业作业的物品，请提前单独说明，确认是否能够承接。</p></div></section>' for i,(k,t,s,d) in enumerate(services,1))+'</div>'+cta()
write('services.html',f'广州搬家服务咨询｜{short}搬家',f'{short}搬家常见需求咨询：居民搬家、小件搬运、办公室搬迁。了解物品清单、现场条件和预约前需核实的事项。',body)
body=pagehero('报价之前，把费用问明白。','车辆、人工和现场条件共同影响搬家费用。对照下面的项目沟通，避免遗漏影响报价的信息。')+'''<article class="wrap section content"><span class="eyebrow">MOVING COST GUIDE</span><div class="answer"><p><strong>广州搬家怎么收费？</strong><br>没有适用于所有家庭或办公室的统一价格。咨询时应核对车辆车次、人工、楼层与搬运距离，以及打包、拆装、特殊物品等项目。具体金额以双方确认的报价为准。</p></div><h2>一份报价，应说明哪些内容？</h2><div class="table-wrap"><table><thead><tr><th scope="col">费用因素</th><th scope="col">需要提供的信息</th><th scope="col">建议确认的问题</th></tr></thead><tbody><tr><td>车辆及车次</td><td>物品数量、体积、路线</td><td>车型是什么？增加车次如何计费？</td></tr><tr><td>人工与时间</td><td>物品重量、现场作业条件</td><td>安排几人？等待或超时是否另计？</td></tr><tr><td>楼层与电梯</td><td>两端楼层、电梯尺寸</td><td>无电梯及大件走楼梯如何计算？</td></tr><tr><td>平面搬运距离</td><td>停车点到门口或电梯的距离</td><td>包含多少距离？超出如何计费？</td></tr><tr><td>拆装与打包</td><td>家具型号、材料与保护需求</td><td>拆装、复装、包装材料是否包含？</td></tr><tr><td>特殊物品</td><td>重量、尺寸、材质和操作要求</td><td>能否承接？需要怎样的保护方案？</td></tr></tbody></table></div><h2>确认前，保留一份书面约定</h2><p>将服务日期、两端位置、物品范围、收费项目、付款方式和变更处理方式确认清楚。现场物品或条件变化时，先核实费用和处理方式，再决定是否增加作业。</p><h2>为什么这里不展示“起步价”？</h2><p>公司尚未提供可核实的统一价目表。只展示一个低价数字，无法反映车辆、人工与现场条件；请依据实际需求询价。</p><div class="related"><a class="text-link" href="contact.html">整理需求再咨询 ↗</a><a class="text-link" href="guide.html">查看搬家准备指南 ↗</a></div></article>'''+cta()
write('pricing.html',f'广州搬家费用怎么算｜{short}搬家费用说明',f'了解广州搬家费用的车辆、人工、楼层、距离、拆装打包等组成因素，以及报价前需要核实的信息。{name}咨询电话{phone}。',body,article=True)
guide_heading={'zhong':'把家的细节，整理进一份清单。','you':'东西不遗漏，搬家少一点忙乱。','sheng':'从物品编号开始，让搬迁更有序。'}[theme]
guide_extra={'zhong':('家具与易碎品','提前拍摄家具外观，记录拆装配件；玻璃、陶瓷等物品分开保护，并明确告知搬运人员。贵重物品自行保管。'),'you':('租房交接','打包前按保留、转赠、处理分类。与房东约定退房检查时间，记录水电读数，检查钥匙、门禁卡和押金交接事项。'),'sheng':('办公室搬迁','按部门和工位编号为箱子、设备及线缆做对应标记。提前完成数据备份，安排设备负责人，确认搬迁后的连接与验收顺序。')}[theme]
body=pagehero(guide_heading,'一份实用的搬家准备指南：把地址、物品、现场条件和交接事项提前理顺。')+f'''<article class="wrap section content"><span class="eyebrow">PREPARATION / MOVING DAY / HANDOVER</span><div class="answer"><p><strong>预约前的关键准备：</strong>列物品清单，核实两端楼层、电梯、停车和物业要求，明确需要拆装或打包的项目，再向搬家公司确认报价和时间。</p></div><h2>01 / 确定日期时</h2><ul><li>协调两端可搬入和搬出的日期，避免只确定一端。</li><li>询问物业搬运时段、车辆登记和电梯预约要求。</li><li>逐房间清点家具、家电、纸箱，记录大型物品尺寸。</li><li>在确认服务前，核实报价包含项及可能的额外费用。</li></ul><h2>02 / 开始打包时</h2><h3>{guide_extra[0]}</h3><p>{guide_extra[1]}</p><ul><li>按房间或用途装箱，在外侧写清内容和目标房间。</li><li>证件、现金、钥匙、药品与当天必需品随身保管。</li><li>不要把过多重物集中在一个纸箱中，封箱前检查承重。</li><li>拍摄接线和零部件位置，配件集中装袋并做好标记。</li></ul><h2>03 / 搬家当天</h2><p>保持通道通畅，向现场人员说明需要重点保护的物品。离开旧址前检查柜内、阳台、储物间和插座旁。出现未约定的作业或费用时，及时沟通确认。</p><h2>04 / 到达新址后</h2><p>按物品清单核对数量，检查家具外观、拆装结果和配件。确认摆放位置，保存报价和沟通记录；发现异常时及时记录并反馈。</p><div class="related"><a class="text-link" href="contact.html">生成我的需求清单 ↗</a><a class="text-link" href="faq.html">查看更多问题 ↗</a></div></article>'''+cta()
write('guide.html',f'广州搬家准备清单与注意事项｜{short}搬家',f'{short}搬家准备指南，涵盖预约前信息、物品分类打包、{guide_extra[0]}、当天检查及到达新址后的交接。',body,article=True)
body=pagehero('关于搬家，把问题问清楚。','从准备信息到报价与验收，整理你在咨询前可能需要的答案。')+'<section class="section"><div class="wrap content">'+faq_html(faqs)+'</div></section>'+cta()
write('faq.html',f'广州搬家常见问题与解答｜{short}搬家',f'广州搬家费用、预约资料、楼层电梯、拆装材料及搬后验收问题解答。联系{name}：{phone}。',body,faqs)
body=pagehero(f'{short}搬家，认识一下。',f'{name}。从一次具体的沟通开始，了解你的搬家需求。')+f'''<section class="section"><div class="wrap split"><div><span class="eyebrow">{english}</span><h2>{label}。</h2><p>{intro}</p><a class="btn" href="tel:{phone}">直接电话沟通 ↗</a></div><div><h3>公司信息</h3><ul class="check-list"><li><div><b>公司名称</b><span>{name}</span></div></li><li><div><b>联系电话</b><a href="tel:{phone}">{phone}</a></div></li>{f'<li><div><b>营业地址</b><span>{esc(C["address"])}</span></div></li>' if C.get('address') else ''}<li><div><b>服务沟通</b><span>请提供两端位置、时间与物品信息，核实具体承接范围。</span></div></li></ul><p class="note">到访安排请先电话联系。</p></div></div></section>'''+cta()
write('about.html',f'关于{name}｜联系方式',f'{name}公司信息与搬家咨询方式，联系电话{phone}。到访安排及具体服务请先电话确认。',body)
body=pagehero('说说你的搬家计划。','直接来电沟通，或先整理一份需求清单，把影响方案的细节一次说清。')+f'''<section class="section"><div class="wrap contact-grid"><div><span class="eyebrow">CONTACT {short}</span><h2>从这里，<br>开始下一程。</h2><p>{name}</p><a class="phone-big" href="tel:{phone}">{phone}</a><p class="note">点击号码拨打电话。具体服务范围、时间与报价，以沟通确认为准。</p><ul class="check-list"><li><div><b>搬出与搬入位置</b><span>说明区域、楼层、电梯和停车条件。</span></div></li><li><div><b>物品与额外需求</b><span>准备数量、尺寸，以及拆装打包要求。</span></div></li></ul></div><div><h3>我的搬家需求清单</h3><p class="note">在当前浏览器生成，可下载后用于沟通。内容不会上传，生成清单不代表已预约。</p><form id="move-form" data-company="{name}" data-phone="{phone}"><div class="form-grid"><label>搬出区域 <span aria-hidden="true">*</span><input name="from" required maxlength="120" placeholder="如：天河区，某小区" autocomplete="off"></label><label>搬入区域 <span aria-hidden="true">*</span><input name="to" required maxlength="120" placeholder="如：海珠区，某小区" autocomplete="off"></label><label>计划日期<input type="date" name="date"></label><label>搬运类型<select name="type"><option>居民搬家</option><option>小件搬运</option><option>办公室搬迁</option><option>其他需求，电话确认</option></select></label><label class="full">楼层 / 电梯情况 <span aria-hidden="true">*</span><input name="floor" required maxlength="150" placeholder="如：搬出 6 楼有电梯，搬入 3 楼无电梯"></label><label class="full">物品清单与其他事项<textarea name="items" rows="4" maxlength="2000" placeholder="如：10 箱行李、1 张床需拆装；小区需提前登记车辆"></textarea></label><div class="full"><button class="btn" type="submit">生成需求清单 ↗</button></div></div></form><div id="plan-result" class="result" role="status" aria-live="polite" hidden><h3>需求清单已生成</h3><pre id="plan-text"></pre><div class="actions"><button type="button" class="btn outline" id="download-plan">下载清单</button><a class="btn" href="tel:{phone}">拨打电话咨询</a></div></div></div></div></section>'''
write('contact.html',f'联系{short}搬家｜{phone}｜搬家需求清单',f'拨打{phone}联系{name}，沟通搬家日期、两端位置和物品信息；也可在本地整理搬家需求清单。',body)
body=pagehero('隐私说明','了解这个网站如何处理你的信息。')+f'''<article class="wrap section content"><h2>需求清单</h2><p>网页中的搬家需求表单仅在你的浏览器内整理文本，不向服务器发送表单内容，也不在本地持久保存。下载清单由浏览器保存为文本文件，请自行保管。</p><h2>电话联系</h2><p>点击电话号码会请求设备打开拨号功能。后续通话及沟通不在本网站内进行。</p><h2>Cookie 与统计</h2><p>当前网站代码未接入广告、第三方统计、跟踪 Cookie 或外部字体。实际部署服务器可能产生基础访问日志，其管理方式应由运营方根据上线环境补充说明。</p><h2>联系我们</h2><p>有关本网站的问题，请拨打 <a href="tel:{phone}">{phone}</a> 联系{name}。</p></article>'''
write('privacy.html',f'隐私说明｜{name}','搬家需求清单的数据处理方式、电话联系及网站隐私说明。',body)
write('404.html',f'页面未找到｜{short}搬家','该页面不存在，请返回首页或联系搬家咨询。',pagehero('这一页，暂时没有找到。','可以返回首页，继续了解搬家服务与咨询方式。')+'<div class="wrap section"><a class="btn" href="index.html">返回首页 ↗</a></div>')
content_pages()
# Generate absolute indexing signals only after a real domain has been configured.
pages=[p.name for p in OUT.glob('*.html') if p.name!='404.html']
robots='User-agent: *\nAllow: /\n'
if domain:
 robots+=f'Sitemap: {domain}/sitemap.xml\n'
 (OUT/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join(f'<url><loc>{esc(domain+"/"+("" if p=="index.html" else p))}</loc></url>' for p in sorted(pages))+'</urlset>')
elif (OUT/'sitemap.xml').exists(): (OUT/'sitemap.xml').unlink()
(OUT/'robots.txt').write_text(robots)
(OUT/'assets'/'favicon.svg').write_text(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="12" fill="{C["color"]}"/><text x="32" y="45" text-anchor="middle" fill="white" font-size="40" font-family="serif">{short[0]}</text></svg>')
print(f'{name}: {len(pages)} pages + 404 generated → {OUT}')
