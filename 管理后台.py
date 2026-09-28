#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Independent content editor and site preview. Run with: python3 管理后台.py"""
import argparse
import getpass
import hashlib
import hmac
import html
import json
import mimetypes
import os
import secrets
import subprocess
import sys
import time
import uuid
import webbrowser
from email.parser import BytesParser
from email import policy
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, quote, unquote, urlsplit

ROOT = Path(__file__).resolve().parent
SITE_CONFIG = json.loads((ROOT / 'site.json').read_text(encoding='utf-8'))
SITE_NAME = SITE_CONFIG['name']
SITE_SLUG = SITE_CONFIG['admin_slug']
COOKIE_NAME = 'admin_session_' + SITE_SLUG
AUTH = ROOT / '.admin-auth.json'
SETUP_TOKEN = secrets.token_urlsafe(24)
MAX_POST = 7 * 1024 * 1024
MAX_IMAGE = 5 * 1024 * 1024
def company_url(site):
    return '/admin/'



def esc(value):
    return html.escape(str(value or ''), quote=True)


def sites():
    return {SITE_NAME: ROOT}


def config():
    return json.loads(AUTH.read_text(encoding='utf-8')) if AUTH.is_file() else None


def write_json(path, obj, private=False):
    tmp = path.with_name(path.name + '.tmp-' + secrets.token_hex(4))
    tmp.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding='utf-8')
    if private:
        os.chmod(tmp, 0o600)
    os.replace(tmp, path)


def password_hash(password, salt):
    return hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), bytes.fromhex(salt), 300_000).hex()


def make_session(conf):
    stamp = str(int(time.time()))
    nonce = secrets.token_hex(16)
    payload = f'{stamp}.{nonce}'
    signature = hmac.new(bytes.fromhex(conf['secret']), payload.encode(), hashlib.sha256).hexdigest()
    return payload + '.' + signature


def valid_session(cookie, conf):
    try:
        stamp, nonce, signature = cookie.split('.')
        if not stamp.isdigit() or int(time.time()) - int(stamp) > 8 * 3600 or int(stamp) > time.time() + 60:
            return False
        payload = f'{stamp}.{nonce}'
        expected = hmac.new(bytes.fromhex(conf['secret']), payload.encode(), hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, signature)
    except (ValueError, AttributeError):
        return False


def csrf_for(cookie, conf):
    return hmac.new(bytes.fromhex(conf['secret']), ('csrf:' + cookie).encode(), hashlib.sha256).hexdigest()


def load_items(folder):
    path = folder / 'content.json'
    return json.loads(path.read_text(encoding='utf-8')) if path.is_file() else []


def admin_layout(title, body, signed_in=False, site=None):
    logout = '<form method="post" action="/admin/logout" class="logout"><input type="hidden" name="csrf" value="__CSRF__"><button type="submit">退出登录</button></form>' if signed_in else ''
    nav = ('<a href="/" target="_blank" rel="noopener">查看官网 ↗</a>') if signed_in else ''
    brand = (site.replace('广州','').replace('有限公司','') + ' · 内容管理') if site else SITE_NAME + ' · 内容管理'
    color = SITE_CONFIG['color']
    return f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)} · 官网管理</title><style>
:root{{--ink:{color};--muted:#647481;--line:#dce3e8;--paper:#f4f7f8}}*{{box-sizing:border-box}}body{{margin:0;background:var(--paper);color:var(--ink);font:16px/1.6 -apple-system,BlinkMacSystemFont,"PingFang SC",sans-serif}}a{{color:inherit}}header{{background:var(--ink);color:#fff;padding:18px max(24px,calc((100vw - 1180px)/2));display:flex;justify-content:space-between;gap:24px;align-items:center}}header strong{{font-size:19px}}header nav{{display:flex;align-items:center;gap:25px;font-size:14px}}header a{{text-decoration:none}}.logout{{margin:0}}.logout button{{border:1px solid #ffffff80;background:none;color:white;padding:7px 12px}}main{{max-width:1180px;margin:50px auto;padding:0 24px 80px}}h1{{font-size:clamp(29px,3vw,42px);line-height:1.25;margin:0 0 12px}}h2{{font-size:23px;margin:0 0 14px}}p{{color:var(--muted)}}.lead{{margin:0 0 32px}}.panel{{background:white;border:1px solid var(--line);padding:30px;margin:24px 0}}.grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:20px}}.card{{background:white;border:1px solid var(--line);padding:26px}}.card h2{{margin:0 0 9px}}.links{{display:flex;gap:16px;flex-wrap:wrap;margin-top:18px}}.links a{{font-size:14px}}.button{{display:inline-block;background:var(--ink);color:white;border:1px solid var(--ink);text-decoration:none;padding:11px 18px;font-size:14px;cursor:pointer}}.button.secondary{{background:white;color:var(--ink)}}button{{cursor:pointer;font:inherit}}label{{display:block;font-size:14px;font-weight:600;margin:18px 0 6px}}input,textarea,select{{display:block;width:100%;padding:12px;border:1px solid #afbec9;border-radius:0;background:white;color:var(--ink);font:inherit}}textarea{{min-height:170px;resize:vertical}}input:focus,textarea:focus,select:focus,button:focus-visible,a:focus-visible{{outline:2px solid #cc7b2f;outline-offset:2px}}.form-row{{display:grid;grid-template-columns:1fr 1fr;gap:20px}}.notice{{padding:12px 16px;background:#e6f2ec;color:#1c5c40;border-left:3px solid #1c5c40;margin:24px 0}}.error{{padding:12px 16px;background:#fff0ed;color:#8d2f1e;border-left:3px solid #8d2f1e;margin:24px 0}}.meta{{font-size:13px;color:var(--muted)}}.table-wrap{{overflow-x:auto}}table{{width:100%;border-collapse:collapse}}th,td{{text-align:left;padding:14px;border-bottom:1px solid var(--line);vertical-align:top}}th{{font-size:13px;color:var(--muted)}}.pill{{font-size:12px;padding:3px 8px;background:#e6edf4;white-space:nowrap}}.pill.live{{background:#e3f2e9;color:#1a6545}}.preview{{max-width:260px;height:auto;display:block;margin:14px 0}}.help{{font-size:13px;color:var(--muted)}}@media(max-width:780px){{header{{padding:16px 20px;display:block}}header nav{{margin-top:12px;flex-wrap:wrap}}main{{margin:28px auto}}.grid,.form-row{{grid-template-columns:1fr}}.panel{{padding:20px}}}}
</style></head><body><header><strong>{esc(brand)}</strong><nav>{nav}{logout}</nav></header><main>{body}</main></body></html>'''


class Handler(BaseHTTPRequestHandler):
    def _session_cookie(self, value, clear=False):
        secure = '; Secure' if self.headers.get('X-Forwarded-Proto') == 'https' else ''
        age = '0' if clear else '28800'
        return f'{COOKIE_NAME}={value}; HttpOnly; SameSite=Strict; Path=/admin; Max-Age={age}{secure}'

    def _cookie(self):
        for part in self.headers.get('Cookie', '').split(';'):
            key, sep, val = part.strip().partition('=')
            if key == COOKIE_NAME and sep:
                return val
        return ''

    def _authorized(self):
        conf = config()
        return bool(conf and valid_session(self._cookie(), conf))

    def _send(self, status, body, content_type='text/html; charset=utf-8', cookie=None):
        data = body.encode('utf-8') if isinstance(body, str) else body
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(data)))
        self.send_header('Cache-Control', 'no-store' if self.path.startswith('/admin/') else 'no-cache')
        self.send_header('X-Content-Type-Options', 'nosniff')
        if self.path.startswith('/admin/'):
            self.send_header('Content-Security-Policy', "default-src 'none'; style-src 'unsafe-inline'; img-src 'self'; form-action 'self'; base-uri 'none'")
        if cookie:
            self.send_header('Set-Cookie', cookie)
        self.end_headers()
        self.wfile.write(data)

    def _redirect(self, target, cookie=None):
        self.send_response(HTTPStatus.SEE_OTHER)
        self.send_header('Location', target)
        if cookie:
            self.send_header('Set-Cookie', cookie)
        self.send_header('Content-Length', '0')
        self.end_headers()

    def _admin_page(self, title, body, status=200, site=None):
        page = admin_layout(title, body, self._authorized(), site)
        conf = config()
        if conf:
            page = page.replace('__CSRF__', csrf_for(self._cookie(), conf))
        self._send(status, page)

    def _query(self):
        return {k: v[0] for k, v in parse_qs(urlsplit(self.path).query, keep_blank_values=True).items()}

    def _static(self, path):
        clean = unquote(path)
        relative = Path(clean.lstrip('/') or 'index.html')
        folder = (ROOT / 'dist').resolve()
        target = (folder / relative).resolve()
        if folder not in target.parents:
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        if target.is_dir():
            target = target / 'index.html'
        if not target.is_file():
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        kind = mimetypes.guess_type(str(target))[0] or 'application/octet-stream'
        if kind.startswith('text/') or kind in ('image/svg+xml', 'application/javascript', 'application/json'):
            kind += '; charset=utf-8'
        self._send(200, target.read_bytes(), kind)

    def do_GET(self):
        path = unquote(urlsplit(self.path).path)
        if path == '/admin':
            self._redirect('/admin/')
            return
        if not path.startswith('/admin/'):
            self._static(path)
            return
        if path not in ('/admin/', '/admin/item', '/admin/delete'):
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        site = SITE_NAME
        label = SITE_CONFIG['short']
        if not config():
            self.send_error(HTTPStatus.SERVICE_UNAVAILABLE, '请在服务器终端运行 --set-password 初始化本公司密码。')
            return
        if not self._authorized():
            body=f'''<h1>{esc(label)}管理员登录</h1><p class="lead">登录后管理新闻资讯与案例。</p><div class="panel"><form method="post" action="/admin/login"><input type="hidden" name="token" value="{SETUP_TOKEN}"><label for="password">密码</label><input id="password" name="password" type="password" autocomplete="current-password" required><p><button class="button" type="submit">登录后台</button></p></form></div>'''
            self._send(200, admin_layout('登录', body, site=site))
            return
        if path == '/admin/':
            self._site_dashboard(site)
        elif path == '/admin/delete':
            self._delete_confirm(site)
        else:
            self._editor(site)

    def _site_dashboard(self,site):
        folder=sites().get(site)
        if not folder:
            self.send_error(HTTPStatus.NOT_FOUND);return
        entries=load_items(folder)
        rows=[]
        for x in entries:
            label='新闻资讯' if x['kind']=='news' else '案例'
            status='<span class="pill live">已发布</span>' if x['status']=='published' else '<span class="pill">草稿</span>'
            rows.append(f'<tr><td>{label}</td><td>{esc(x["title"])}</td><td>{status}</td><td><a href="{company_url(site)}item?id={esc(x["id"])}">编辑</a></td></tr>')
        table='<div class="table-wrap"><table><thead><tr><th>栏目</th><th>标题</th><th>状态</th><th>操作</th></tr></thead><tbody>'+''.join(rows)+'</tbody></table></div>' if rows else '<p>这家公司还没有发布内容。可先创建草稿。</p>'
        base=company_url(site)
        body=f'''<h1>{esc(site)}后台</h1><p class="lead">管理本公司的新闻资讯与案例。</p><div class="links"><a class="button" href="{base}item?kind=news">+ 新增新闻资讯</a><a class="button secondary" href="{base}item?kind=case">+ 新增案例</a></div><section class="panel"><h2>内容列表</h2>{table}</section>'''
        self._admin_page(site+'后台',body,site=site)

    def _editor(self,site):
        q=self._query(); folder=sites().get(site)
        if not folder:
            self.send_error(HTTPStatus.NOT_FOUND);return
        item=next((x for x in load_items(folder) if x['id']==q.get('id')),None)
        kind=item['kind'] if item else q.get('kind','news')
        if kind not in ('news','case'):
            self.send_error(HTTPStatus.BAD_REQUEST);return
        title='编辑内容' if item else ('新建新闻资讯' if kind=='news' else '新建案例')
        current=item or {}
        image=''
        if current.get('image'):
            image=f'<img class="preview" src="/{esc(current["image"])}" alt="当前配图">'
        notice='<div class="notice">已保存，前台页面已更新。</div>' if q.get('saved')=='1' else ''
        base=company_url(site)
        body=f'''<a href="{base}">← 返回{esc(site)}后台</a><h1 style="margin-top:24px">{title}</h1><p class="lead">{esc(site)} · {'新闻资讯' if kind=='news' else '搬家案例'}</p>{notice}<div class="panel"><form method="post" action="{base}save" enctype="multipart/form-data"><input type="hidden" name="csrf" value="__CSRF__"><input type="hidden" name="site" value="{esc(site)}"><input type="hidden" name="kind" value="{kind}"><input type="hidden" name="id" value="{esc(current.get('id'))}"><label for="title">标题 *</label><input id="title" name="title" maxlength="110" value="{esc(current.get('title'))}" required><label for="summary">摘要 *</label><textarea id="summary" name="summary" maxlength="240" style="min-height:85px" required>{esc(current.get('summary'))}</textarea><label for="body">正文 *</label><textarea id="body" name="body" maxlength="20000" rows="13" required>{esc(current.get('body'))}</textarea><p class="help">使用空行分隔段落。正文按纯文本显示，不支持 HTML。</p><div class="form-row"><div><label for="image">配图</label><input id="image" name="image" type="file" accept="image/jpeg,image/png,image/webp"><p class="help">JPG、PNG 或 WebP，最大 5 MB。新图片会替换当前显示的配图。</p>{image}</div><div><label for="image_alt">图片说明</label><input id="image_alt" name="image_alt" maxlength="140" value="{esc(current.get('image_alt'))}" placeholder="简述画面内容"></div></div><label for="status">状态</label><select id="status" name="status"><option value="draft" {'selected' if current.get('status')!='published' else ''}>草稿：仅后台可见</option><option value="published" {'selected' if current.get('status')=='published' else ''}>发布：更新前台</option></select><p style="margin-top:24px"><button class="button" type="submit">保存内容</button> <a class="button secondary" href="{base}">取消</a></p></form></div>'''
        if item:
            body += f'<p><a href="{base}delete?id={esc(item["id"])}">删除这篇内容</a></p>'
        self._admin_page(title,body,site=site)

    def _delete_confirm(self, site):
        item_id = self._query().get('id', '')
        item = next((x for x in load_items(ROOT) if x['id'] == item_id), None)
        if not item:
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        body = f'''<h1>确认删除</h1><p class="lead">{esc(site)} · {esc(item['title'])}</p><div class="panel"><p>删除后，这篇内容会从后台和官网撤下，无法在后台恢复。</p><form method="post" action="/admin/delete"><input type="hidden" name="csrf" value="__CSRF__"><input type="hidden" name="id" value="{esc(item_id)}"><button class="button" type="submit">确认删除</button> <a class="button secondary" href="/admin/item?id={esc(item_id)}">取消</a></form></div>'''
        self._admin_page('确认删除', body, site=site)

    def _form(self):
        length=int(self.headers.get('Content-Length','0'))
        if length<=0 or length>MAX_POST:
            raise ValueError('上传内容不能超过 7 MB。')
        raw=self.rfile.read(length)
        ctype=self.headers.get('Content-Type','')
        if ctype.startswith('multipart/form-data'):
            message=BytesParser(policy=policy.default).parsebytes(('Content-Type: '+ctype+'\r\nMIME-Version: 1.0\r\n\r\n').encode()+raw)
            if not message.is_multipart():
                raise ValueError('表单格式无效。')
            fields={}; uploads={}
            for part in message.iter_parts():
                key=part.get_param('name',header='content-disposition')
                if not key:continue
                filename=part.get_filename()
                data=part.get_payload(decode=True) or b''
                if filename:
                    uploads[key]=(filename,data)
                else:
                    fields[key]=data.decode('utf-8')
            return fields,uploads
        if ctype.startswith('application/x-www-form-urlencoded'):
            return {k:v[0] for k,v in parse_qs(raw.decode('utf-8'),keep_blank_values=True).items()},{}
        raise ValueError('表单格式无效。')

    def do_POST(self):
        path=urlsplit(self.path).path
        if path not in ('/admin/login','/admin/logout','/admin/save','/admin/delete'):
            self.send_error(HTTPStatus.NOT_FOUND);return
        try:
            fields,uploads=self._form()
            conf=config()
            if not conf:raise ValueError('请先设置管理员密码。')
            if path=='/admin/login':
                if not hmac.compare_digest(fields.get('token',''),SETUP_TOKEN):raise ValueError('登录请求无效。')
                if not hmac.compare_digest(password_hash(fields.get('password',''),conf['salt']),conf['password_hash']):
                    time.sleep(0.5)
                    raise ValueError('密码错误。')
                cookie=make_session(conf)
                self._redirect('/admin/', self._session_cookie(cookie))
                return
            cookie=self._cookie()
            if not valid_session(cookie,conf) or not hmac.compare_digest(fields.get('csrf',''),csrf_for(cookie,conf)):
                raise ValueError('登录状态已失效，请重新登录。')
            if path=='/admin/logout':
                self._redirect('/admin/', self._session_cookie('', clear=True))
                return
            if path=='/admin/delete':
                self._delete(fields)
                return
            self._save(fields,uploads,SITE_NAME)
        except (ValueError,UnicodeDecodeError,KeyError,json.JSONDecodeError) as error:
            self._admin_page('无法保存',f'<h1>无法完成操作</h1><div class="error">{esc(error)}</div><p><a href="/admin/">返回后台</a></p>',400)

    def _save(self,fields,uploads,expected_site=None):
        site=fields.get('site',''); folder=sites().get(site)
        if expected_site and site!=expected_site:raise ValueError('当前公司与内容不一致。')
        if not folder:raise ValueError('未找到公司。')
        kind=fields.get('kind',''); status=fields.get('status','')
        if kind not in ('news','case') or status not in ('draft','published'):
            raise ValueError('栏目或状态无效。')
        title=fields.get('title','').strip();summary=fields.get('summary','').strip();body=fields.get('body','').strip();image_alt=fields.get('image_alt','').strip()
        if not (1<=len(title)<=110 and 1<=len(summary)<=240 and 1<=len(body)<=20000 and len(image_alt)<=140):
            raise ValueError('请填写标题、摘要和正文，并检查字数限制。')
        entries=load_items(folder);id_=fields.get('id','')
        item=next((x for x in entries if x['id']==id_),None) if id_ else None
        if id_ and not item:raise ValueError('原内容不存在，请返回列表重试。')
        if item and item['kind']!=kind:raise ValueError('不能修改栏目类型。')
        now=time.strftime('%Y-%m-%dT%H:%M:%S%z')
        if not item:
            id_=uuid.uuid4().hex[:12]
            item={'id':id_,'kind':kind,'created_at':now,'image':''}
            entries.append(item)
        uploaded=uploads.get('image')
        if uploaded:
            _,data=uploaded
            if len(data)>MAX_IMAGE:raise ValueError('图片不能超过 5 MB。')
            if data.startswith(b'\xff\xd8\xff') and data.endswith(b'\xff\xd9'):ext='jpg'
            elif data.startswith(b'\x89PNG\r\n\x1a\n'):ext='png'
            elif len(data)>=12 and data[:4]==b'RIFF' and data[8:12]==b'WEBP':ext='webp'
            else:raise ValueError('只支持有效的 JPG、PNG 或 WebP 图片。')
            upload_dir=folder/'assets'/'uploads';upload_dir.mkdir(parents=True,exist_ok=True)
            filename=uuid.uuid4().hex+'.'+ext
            (upload_dir/filename).write_bytes(data)
            item['image']='assets/uploads/'+filename
        item.update(title=title,summary=summary,body=body,image_alt=image_alt,status=status,updated_at=now)
        if status=='published' and not item.get('published_at'):
            item['published_at']=now
        write_json(folder/'content.json',entries)
        subprocess.run([sys.executable,str(folder/'build.py')],check=True,cwd=str(folder),capture_output=True,text=True)
        self._redirect(company_url(site)+'item?id='+quote(id_)+'&saved=1')

    def _delete(self, fields):
        item_id = fields.get('id', '')
        entries = load_items(ROOT)
        item = next((x for x in entries if x['id'] == item_id), None)
        if not item:
            raise ValueError('内容不存在或已删除。')
        entries.remove(item)
        write_json(ROOT / 'content.json', entries)
        subprocess.run([sys.executable, str(ROOT / 'build.py')], check=True, cwd=str(ROOT), capture_output=True, text=True)
        image = item.get('image', '')
        if image.startswith('assets/uploads/') and image not in (x.get('image') for x in entries):
            filename = Path(image).name
            if image == 'assets/uploads/' + filename:
                for file in (ROOT / 'assets' / 'uploads' / filename, ROOT / 'dist' / 'assets' / 'uploads' / filename):
                    file.unlink(missing_ok=True)
        self._redirect('/admin/')


def main():
    parser=argparse.ArgumentParser(description=SITE_NAME + ' independent content manager')
    parser.add_argument('--port',type=int,default=0,help='Local port; default chooses an available port')
    parser.add_argument('--no-browser',action='store_true')
    parser.add_argument('--set-password',action='store_true',help='Set this company backend password and invalidate sessions')
    args=parser.parse_args()
    if not (ROOT / 'build.py').is_file():raise SystemExit('未找到网站构建脚本。')
    if args.set_password:
        password = getpass.getpass('新密码（至少 12 位）：')
        confirm = getpass.getpass('再次输入：')
        if len(password) < 12 or password != confirm:
            raise SystemExit('密码至少 12 位，且两次输入必须一致。')
        salt = secrets.token_hex(16)
        write_json(AUTH, {
            'salt': salt,
            'password_hash': password_hash(password, salt),
            'secret': secrets.token_hex(32),
        }, private=True)
        print(SITE_NAME + '密码已更新，旧会话已失效。')
        return
    if not AUTH.is_file():
        raise SystemExit('未设置管理员密码；请先运行 python3 管理后台.py --set-password。')
    with ThreadingHTTPServer(('127.0.0.1',args.port),Handler) as server:
        url=f'http://127.0.0.1:{server.server_port}/admin/'
        print(SITE_NAME+'管理后台：'+url,flush=True)
        print('网站预览：'+url.replace('/admin/','/'),flush=True)
        print('保持这个窗口打开；结束时按 Control+C。',flush=True)
        if not args.no_browser:webbrowser.open(url)
        try:server.serve_forever()
        except KeyboardInterrupt:pass


if __name__=='__main__':main()
