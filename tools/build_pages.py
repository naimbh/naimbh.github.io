#!/usr/bin/env python3
"""Build one real page per nav section, for naimbh.com and dev.naimbh.com.

index.html (and dev/index.html) stay the single source of truth. This script
copies each section into its own page (/research/, /portfolio/ ...) with its own
title, description, canonical URL, social tags, structured data and sitemap
entry, so search engines can show them as separate results (sitelinks).

Run it after every edit to index.html or dev/index.html:

    python3 tools/build_pages.py
"""
import datetime
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TODAY = datetime.date.today().isoformat()
PERSON = "https://naimbh.com/#person"

SITES = [
    {
        "src": "index.html",
        "out": "",
        "base": "https://naimbh.com",
        "home_name": "Naim Bin Hasan",
        "home_label": "All of naimbh.com",
        "heading": r'<h2 class="sec',
        "sitemap": "sitemap-main.xml",
        "pages": [
            {"slug": "research", "ids": ["research"], "label": "Research",
             "title": "Research Interests | Naim Bin Hasan, Syracuse University",
             "desc": "Naim Bin Hasan's research on AI and the future of work, human-computer interaction (HCI), digital labor and online freelancers, and ICT for development (ICT4D)."},
            {"slug": "education", "ids": ["education"], "label": "Education",
             "title": "Education | Naim Bin Hasan, PhD in IT at Syracuse University",
             "desc": "Education of Naim Bin Hasan: PhD in Information Science and Technology at the Syracuse University iSchool, MA in Sociology at Florida Atlantic University, and BSS and MSS at the University of Dhaka."},
            {"slug": "experience", "ids": ["work"], "label": "Experience",
             "title": "Experience | Naim Bin Hasan, Researcher & Developer",
             "desc": "Research, teaching and software engineering experience of Naim Bin Hasan, from the Syracuse University iSchool and Florida Atlantic University to full-stack development work."},
            {"slug": "publications", "ids": ["writing"], "label": "Publications",
             "title": "Publications & Talks | Naim Bin Hasan",
             "desc": "Peer-reviewed journal articles, master's thesis and conference talks by Naim Bin Hasan (Hasan, N. B.) on AI, digital labor and Bangladeshi online freelancers.",
             "jsonld": ["ScholarlyArticle", "Thesis"]},
            {"slug": "awards", "ids": ["recognition"], "label": "Awards",
             "title": "Awards & Fellowships | Naim Bin Hasan",
             "desc": "Funding, fellowships and awards received by Naim Bin Hasan, including a Purdue Graduate Excellence Fellowship offer, the FAU Sociology Graduate Student Achievement Award and an AIBS fellowship."},
            {"slug": "projects", "ids": ["projects", "toolkit"], "label": "Projects",
             "title": "Projects, Methods & Stack | Naim Bin Hasan",
             "desc": "Applied systems built by Naim Bin Hasan, custom CMSs, SaaS and real-time apps, plus the research methods and software stack he works with."},
            {"slug": "gallery", "ids": ["gallery"], "label": "Gallery", "type": "CollectionPage",
             "title": "Photos of Naim Bin Hasan | Gallery",
             "desc": "Photos of Naim Bin Hasan at Syracuse University, Florida Atlantic University, the University of Dhaka, conferences and PhD visits.",
             "jsonld": ["ImageGallery"], "images": "/images/gallery/"},
            {"slug": "contact", "ids": ["contact"], "label": "Contact", "type": "ContactPage",
             "title": "Contact Naim Bin Hasan | Syracuse University iSchool",
             "desc": "Contact Naim Bin Hasan, PhD researcher at the Syracuse University School of Information Studies (iSchool), 337 Hinds Hall, Syracuse, NY 13244."},
        ],
    },
    {
        "src": "dev/index.html",
        "out": "dev",
        "base": "https://dev.naimbh.com",
        "home_name": "Naim Bin Hasan, Web Developer",
        "home_label": "Developer home",
        "heading": r'<h2 class="rv"',
        "sitemap": "dev/sitemap.xml",
        "pages": [
            {"slug": "experience", "ids": ["experience"], "label": "Experience",
             "title": "Web Development Experience | Naim Bin Hasan",
             "desc": "Where Naim Bin Hasan has built software: research web tools at the Syracuse University iSchool, full-stack business apps and dashboards at Zilberman Insurance, and 100+ client projects on Upwork and Fiverr."},
            {"slug": "services", "ids": ["services", "@vibe-h"], "label": "Services",
             "title": "Web App, SaaS & CMS Development Services | Naim Bin Hasan",
             "desc": "Scalable custom web apps and SaaS products, SEO-friendly CMS websites, dashboards, e-commerce and API integrations, built with the latest technologies by full-stack developer Naim Bin Hasan."},
            {"slug": "portfolio", "ids": ["work"], "label": "Portfolio",
             "title": "Portfolio | Naim Bin Hasan, Full-Stack Web Developer",
             "desc": "Full-stack projects shipped by Naim Bin Hasan: custom CMSs, SaaS platforms, payments, real-time apps and API integrations, built to scale and to rank.",
             "images": "/images/projects/"},
            {"slug": "reviews", "ids": ["reviews"], "label": "Reviews",
             "title": "Client Reviews | Naim Bin Hasan, Top Rated on Upwork",
             "desc": "Verified five-star client reviews of Naim Bin Hasan's web development work from completed Upwork contracts."},
            {"slug": "stack", "ids": ["stack"], "label": "Stack",
             "title": "Tech Stack | Naim Bin Hasan, Full-Stack Web Developer",
             "desc": "The technologies Naim Bin Hasan builds with: Laravel, PHP, Vue.js, React, MySQL, Redis, Linux servers, Nginx, Docker, AWS S3, Stripe, Twilio and AI-assisted development."},
            {"slug": "process", "ids": ["process"], "label": "Process",
             "title": "How I Work | Naim Bin Hasan, Freelance Web Developer",
             "desc": "A simple, no-surprises process: brief, written scope and quote, build in milestones, then launch and handover with documentation."},
            {"slug": "faq", "ids": ["faq"], "label": "FAQ",
             "title": "FAQ | Hiring Naim Bin Hasan, Freelance Web Developer",
             "desc": "Answers about hiring Naim Bin Hasan: the projects he takes on, how to hire him, which technology he uses, AI-assisted development and freelancing alongside a PhD."},
            {"slug": "contact", "ids": ["contact"], "label": "Contact", "type": "ContactPage",
             "title": "Hire Naim Bin Hasan | Full-Stack Web Developer for Your Project",
             "desc": "Hire Naim Bin Hasan for your web project through Upwork, Fiverr or email. Tell him what you're building, your timeline and budget; he usually replies within a day."},
        ],
    },
]


def find_section(s, key):
    """Return (start, end) of the top-level <section> with this id (or aria-labelledby for '@x')."""
    attr = f'aria-labelledby="{key[1:]}"' if key.startswith("@") else f'id="{key}"'
    m = re.search(r'<section\b[^>]*' + re.escape(attr), s)
    if not m:
        raise SystemExit(f"section not found: {key}")
    depth, i = 0, m.start()
    for t in re.finditer(r'<(/?)section\b', s[m.start():]):
        depth += -1 if t.group(1) else 1
        if depth == 0:
            end = s.index(">", m.start() + t.start()) + 1
            return m.start(), end
    raise SystemExit(f"unbalanced section: {key}")


def set_meta(head, pattern, value):
    new, n = re.subn(pattern, lambda m: m.group(1) + value.replace("&", "&amp;").replace('"', "&quot;") + m.group(2), head, count=1)
    if n != 1:
        raise SystemExit(f"meta not found: {pattern}")
    return new


def build(site):
    src = open(os.path.join(ROOT, site["src"]), encoding="utf-8").read()
    base, pages = site["base"], site["pages"]
    head = src[:src.index("</head>")]
    pre = src[src.index("</head>"):src.index("<main>") + len("<main>")]
    post = src[src.index("</main>"):]
    graph = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', head, re.S).group(1))["@graph"]
    website = next(n["@id"] for n in graph if n["@type"] == "WebSite")

    # which page each section id lives on
    where = {i.lstrip("@"): p["slug"] for p in pages for i in p["ids"]}
    where["top"] = ""

    for n, page in enumerate(pages):
        url = f'{base}/{page["slug"]}/'
        first = page["ids"][0]

        # ---------- <head> ----------
        h = head
        h = re.sub(r'<link rel="preload" as="image"[^>]*>\n', "", h)  # hero photo is not on this page
        h = re.sub(r'<meta property="profile:[^>]*>\n', "", h)
        h = set_meta(h, r'(<title>)[^<]*(</title>)', page["title"])
        h = set_meta(h, r'(<meta name="description" content=")[^"]*(">)', page["desc"])
        h = set_meta(h, r'(<link rel="canonical" href=")[^"]*(">)', url)
        h = set_meta(h, r'(<meta property="og:url" content=")[^"]*(">)', url)
        h = set_meta(h, r'(<meta property="og:type" content=")[^"]*(">)', "website")
        h = set_meta(h, r'(<meta property="og:title" content=")[^"]*(">)', page["title"])
        h = set_meta(h, r'(<meta property="og:description" content=")[^"]*(">)', page["desc"])
        h = set_meta(h, r'(<meta name="twitter:title" content=")[^"]*(">)', page["title"])
        h = set_meta(h, r'(<meta name="twitter:description" content=")[^"]*(">)', page["desc"])
        ld = [
            {"@type": page.get("type", "WebPage"), "@id": url + "#webpage", "url": url,
             "name": page["title"], "description": page["desc"], "inLanguage": "en",
             "isPartOf": {"@id": website}, "about": {"@id": PERSON},
             "breadcrumb": {"@id": url + "#breadcrumb"}, "dateModified": TODAY},
            {"@type": "BreadcrumbList", "@id": url + "#breadcrumb", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": site["home_name"], "item": base + "/"},
                {"@type": "ListItem", "position": 2, "name": page["label"], "item": url}]},
        ] + [node for node in graph if node["@type"] in page.get("jsonld", [])]
        ld_txt = json.dumps({"@context": "https://schema.org", "@graph": ld}, indent=2, ensure_ascii=False)
        h = re.sub(r'(<script type="application/ld\+json">).*?(</script>)',
                   lambda m: m.group(1) + "\n" + ld_txt + "\n" + m.group(2), h, count=1, flags=re.S)

        # ---------- header ----------
        b = pre
        b = re.sub(r'(<a class="skip" href=")#[^"]*', r"\1#" + first.lstrip("@"), b)
        b = re.sub(r'\n<div class="rail".*?</div>\n', "\n", b, flags=re.S)
        def current(m):
            tag = m.group(0)
            if 'class="' in tag:
                return tag.replace('class="', 'class="on ', 1)[:-1] + ' aria-current="page">'
            return tag[:-1] + ' class="on" aria-current="page">'
        b = re.sub(r'<a [^>]*href="/%s/" data-sec="%s"[^>]*>' % (page["slug"], first), current, b)
        b = b.replace("<main>", '<main class="sub">')

        # ---------- the section(s) ----------
        chunks = []
        for k in page["ids"]:
            a, z = find_section(src, k)
            chunks.append(src[a:z])
        body = '\n\n<div class="rule"></div>\n\n'.join(chunks) if site["out"] == "" else "\n\n".join(chunks)
        if "gallery" in page["ids"]:  # the photo viewer sits right after the gallery section
            body += "\n\n" + re.search(r'<dialog class="lb".*?</dialog>', src, re.S).group(0)
        # the page heading becomes the <h1>
        hm = re.search(site["heading"], body)
        close = body.index("</h2>", hm.start())
        body = body[:hm.start()] + "<h1" + body[hm.start() + 3:close] + "</h1>" + body[close + 5:]

        # in-page links to sections that now live on other pages
        own = {i.lstrip("@") for i in page["ids"]}

        def fix(m):
            t = m.group(1)
            if t in own or re.search(r'id="%s"' % re.escape(t), body):
                return m.group(0)
            if t in where:
                return f'href="/{where[t]}/"' if where[t] else 'href="/"'
            return f'href="/#{t}"'
        body = re.sub(r'href="#([\w-]+)"', fix, body)

        prev_p, next_p = pages[n - 1] if n else None, pages[n + 1] if n + 1 < len(pages) else None
        more = '<nav class="wrap pg-more" aria-label="More pages">'
        more += f'<a href="/{prev_p["slug"]}/">← {prev_p["label"]}</a>' if prev_p else "<span></span>"
        more += f'<a class="home" href="/">{site["home_label"]}</a>'
        more += f'<a href="/{next_p["slug"]}/">{next_p["label"]} →</a>' if next_p else "<span></span>"
        more += "</nav>"

        html = h + b + "\n" + body + "\n\n" + more + "\n" + post
        out = os.path.join(ROOT, site["out"], page["slug"])
        os.makedirs(out, exist_ok=True)
        open(os.path.join(out, "index.html"), "w", encoding="utf-8").write(html)
        print("built", url)

    # ---------- sitemap ----------
    path = os.path.join(ROOT, site["sitemap"])
    sm = open(path, encoding="utf-8").read()
    sm = re.sub(r"\s*<!-- section pages: tools/build_pages.py -->.*?<!-- /section pages -->", "", sm, flags=re.S)
    home_imgs = re.findall(r"\s*<image:image>.*?</image:image>", sm, re.S)
    entries = []
    for page in pages:
        imgs = "".join(i for i in home_imgs if page.get("images") and page["images"] in i)
        entries.append(f'  <url>\n    <loc>{base}/{page["slug"]}/</loc>\n    <lastmod>{TODAY}</lastmod>\n'
                       f'    <changefreq>monthly</changefreq>\n    <priority>0.8</priority>{imgs}\n  </url>')
    block = "\n  <!-- section pages: tools/build_pages.py -->\n" + "\n".join(entries) + "\n  <!-- /section pages -->\n"
    sm = sm.replace("\n</urlset>", block + "</urlset>")
    open(path, "w", encoding="utf-8").write(sm)
    print("sitemap", site["sitemap"], len(pages), "pages")


if __name__ == "__main__":
    for s in SITES:
        build(s)
