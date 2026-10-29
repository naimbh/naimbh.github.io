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
import hashlib
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
        "intro_class": "sec-note pg-intro reveal",
        "sitemap": "sitemap-main.xml",
        "pages": [
            {"slug": "research", "ids": ["research"], "label": "Research",
             "title": "Research Interests | Naim Bin Hasan, Syracuse University",
             "desc": "Naim Bin Hasan's research on AI and the future of work, human-computer interaction (HCI), digital labor and online freelancers, and ICT4D.",
             "h1": "Research interests of Naim Bin Hasan",},
            {"slug": "education", "ids": ["education"], "label": "Education",
             "title": "Education | Naim Bin Hasan, Syracuse iSchool PhD Researcher",
             "desc": "Education of Naim Bin Hasan: a PhD in Information Science and Technology at Syracuse, an MA in Sociology at FAU and two sociology degrees from Dhaka.",
             "h1": "Education of Naim Bin Hasan",
             "intro": "Naim Bin Hasan began a fully funded PhD in Information Science and Technology at the Syracuse University iSchool in fall 2026. He holds an MA in Sociology from Florida Atlantic University (2024–2026), where his thesis studied Bangladeshi online freelancers, and a BSS (Honours) and an MSS in Sociology from the University of Dhaka."},
            {"slug": "experience", "ids": ["work"], "label": "Experience",
             "title": "Experience | Naim Bin Hasan, Researcher & Developer",
             "desc": "Naim Bin Hasan's research, teaching and software experience at the Syracuse University iSchool, Florida Atlantic University and Zilberman Insurance.",
             "h1": "Research, teaching and software experience",
             "intro": "Naim Bin Hasan is a Graduate Research Assistant at the Syracuse University iSchool, where he works on Gravity Spy. Before that, he was a Graduate Teaching Assistant in the Department of Sociology at Florida Atlantic University and, earlier, a full-stack developer: Lead Full-Stack Developer at Zilberman Insurance and a Top Rated freelancer with 100+ projects on Upwork and Fiverr."},
            {"slug": "publications", "ids": ["writing"], "label": "Publications",
             "title": "Publications & Talks | Naim Bin Hasan",
             "desc": "Peer-reviewed research, a master's thesis and conference talks by Naim Bin Hasan (Hasan, N. B.) on AI, digital labor and online freelancers.",
             "jsonld": ["ScholarlyArticle", "Thesis"],
             "h1": "Publications and talks by Naim Bin Hasan",
             "intro": "Naim Bin Hasan (cited as Hasan, N. B.) writes about AI, work and digital labor. His peer-reviewed article \u201cAI Efficiency vs Human Empathy\u201d appeared in Sociology Lens (Wiley) in 2025, and his 2026 master's thesis, \u201cTrading Precarities,\u201d studies how Bangladeshi freelancers use the digital economy amid local insecurity and AI disruption."},
            {"slug": "awards", "ids": ["recognition"], "label": "Awards",
             "title": "Awards & Fellowships | Naim Bin Hasan",
             "desc": "Naim Bin Hasan's awards and fellowships, including the FAU Sociology Graduate Student Achievement Award, an AIBS Fellowship and a Purdue fellowship offer.",
             "h1": "Awards and fellowships of Naim Bin Hasan",
             "intro": "Naim Bin Hasan's recognition includes the Sociology Graduate Student Achievement Award at Florida Atlantic University (2026), a Provost's Certificate of Recognition for Publishing (2026), an American Institute of Bangladesh Studies (AIBS) Fellowship for thesis fieldwork (2025), and a Graduate Excellence Fellowship offer from Purdue University, which he declined to join Syracuse."},
            {"slug": "projects", "ids": ["projects", "toolkit"], "label": "Projects",
             "title": "Software Projects, Methods & Stack | Naim Bin Hasan",
             "desc": "Applied systems built by Naim Bin Hasan, custom CMSs, SaaS and real-time apps, plus the research methods and software stack he works with.",
             "h1": "Software projects by Naim Bin Hasan",
             "intro": "Alongside his research, Naim Bin Hasan builds full-stack web platforms: content management systems for a nonprofit and a law firm, a scholarly journal platform, an EdTech SaaS, a restaurant ordering system and a real-time chat app. This page lists selected systems, followed by the research methods and software tools he uses."},
            {"slug": "gallery", "ids": ["gallery"], "label": "Gallery", "type": "CollectionPage",
             "title": "Photos of Naim Bin Hasan | Gallery",
             "desc": "Photos of Naim Bin Hasan at Syracuse University, Florida Atlantic University, the University of Dhaka, conferences and PhD visits.",
             "jsonld": ["ImageGallery"], "images": "/images/gallery/", "h1": "Photos of Naim Bin Hasan"},
            {"slug": "contact", "ids": ["contact"], "label": "Contact", "type": "ContactPage",
             "title": "Contact Naim Bin Hasan | Syracuse University iSchool",
             "desc": "Contact Naim Bin Hasan, PhD researcher at the Syracuse University School of Information Studies (iSchool), 337 Hinds Hall, Syracuse, NY 13244.",
             "h1": "Contact Naim Bin Hasan"},
        ],
    },
    {
        "src": "dev/index.html",
        "out": "dev",
        "base": "https://dev.naimbh.com",
        "home_name": "Naim Bin Hasan, Web Developer",
        "home_label": "Developer home",
        "heading": r'<h2 class="rv"',
        "intro_class": "note pg-intro rv",
        "sitemap": "dev/sitemap.xml",
        "pages": [
            {"slug": "experience", "ids": ["experience"], "label": "Experience",
             "title": "Web Development Experience | Naim Bin Hasan",
             "desc": "Where Naim Bin Hasan has built software: research tools at the Syracuse iSchool, business apps at Zilberman Insurance and 100+ Upwork and Fiverr projects.",
             "h1": "Web development experience",
             "intro": "Naim Bin Hasan has built software professionally since 2019: as a freelance full-stack developer on Upwork and Fiverr (Top Rated, 100% Job Success, 100+ projects), as a junior and then lead developer at Zilberman Insurance, and now as a builder of research web tools at the Syracuse University iSchool."},
            {"slug": "services", "ids": ["services", "@vibe-h"], "label": "Services",
             "title": "Web App, SaaS & CMS Development Services | Naim Bin Hasan",
             "desc": "Custom web apps, SaaS products, SEO-friendly CMS websites, dashboards, e-commerce and API integrations from freelance full-stack developer Naim Bin Hasan.",
             "jsonld": ["ProfessionalService"],
             "h1": "Web app, SaaS and CMS development services",
             "intro": "Naim Bin Hasan is a freelance full-stack developer who builds custom web apps and SaaS products, SEO-friendly CMS websites, dashboards, e-commerce and API integrations for businesses and nonprofits. Every project is scoped in writing, delivered in milestones and handed over with documentation."},
            {"slug": "portfolio", "ids": ["work"], "label": "Portfolio",
             "title": "Portfolio | Naim Bin Hasan, Full-Stack Web Developer",
             "desc": "Full-stack projects shipped by Naim Bin Hasan: custom CMSs, SaaS platforms, payments, real-time apps and API integrations, built to scale and to rank.",
             "images": "/images/projects/", "jsonld": ["ProfessionalService"],
             "h1": "Web development portfolio: projects I've shipped",
             "intro": "Selected full-stack projects by Naim Bin Hasan, including live CMS websites for a Bangladeshi nonprofit (dohps.org) and a trilingual law firm (shaiderlaw.com), a scholarly journal platform, an EdTech SaaS, restaurant ordering with Stripe and DoorDash, and a real-time chat app."},
            {"slug": "reviews", "ids": ["reviews"], "label": "Reviews",
             "title": "Client Reviews | Naim Bin Hasan, Top Rated on Upwork",
             "desc": "Five-star client reviews of Naim Bin Hasan's web development work from completed Upwork contracts, where he is Top Rated with 100% Job Success.",
             "h1": "Client reviews of Naim Bin Hasan",
             "intro": "Feedback from clients on completed Upwork contracts. Naim Bin Hasan holds Top Rated status and a 100% Job Success score on Upwork, where his full review history is public."},
            {"slug": "stack", "ids": ["stack"], "label": "Stack",
             "title": "Tech Stack | Naim Bin Hasan, Full-Stack Web Developer",
             "desc": "The tools Naim Bin Hasan builds with: Laravel, PHP, Vue.js, React, MySQL, Redis, Nginx, Docker, AWS S3, Stripe, Twilio and AI-assisted development.",
             "h1": "Tech stack: the tools I use every day"},
            {"slug": "process", "ids": ["process"], "label": "Process",
             "title": "How I Work | Naim Bin Hasan, Freelance Web Developer",
             "desc": "How Naim Bin Hasan runs a web project: a brief, a written scope and quote, a build in clickable milestones, then launch and handover with documentation.",
             "h1": "How I work: a simple, no-surprises process",
             "intro": "Every project with Naim Bin Hasan follows four steps: a brief, a written scope and quote, a build delivered in clickable milestones, and a launch with handover and documentation. You can choose fixed-price milestones or an hourly estimate."},
            {"slug": "faq", "ids": ["faq"], "label": "FAQ",
             "title": "FAQ | Hiring Naim Bin Hasan, Freelance Web Developer",
             "desc": "Answers about hiring Naim Bin Hasan: projects he takes on, how to hire him, technology choices, AI-assisted development and freelancing during a PhD.",
             "jsonld": ["FAQPage"],
             "h1": "FAQ: hiring a freelance full-stack developer"},
            {"slug": "contact", "ids": ["contact"], "label": "Contact", "type": "ContactPage",
             "title": "Hire Naim Bin Hasan | Full-Stack Developer for Your Project",
             "desc": "Hire Naim Bin Hasan through Upwork, Fiverr or email. Share what you're building, your timeline and your budget; he usually replies within a day.",
             "h1": "Have a project? Hire Naim Bin Hasan."},
        ],
    },
]


DATES = os.path.join(ROOT, "tools", "page-dates.json")


def load_dates():
    try:
        return json.load(open(DATES, encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def changed_on(dates, url, content):
    """Date this content last changed: kept while its hash is the same, today when it changes."""
    digest = hashlib.sha1(content.encode("utf-8")).hexdigest()
    rec = dates.get(url)
    if not rec or rec["hash"] != digest:
        rec = dates[url] = {"hash": digest, "date": TODAY}
    return rec["date"]


def types_of(node):
    t = node.get("@type")
    return t if isinstance(t, list) else [t]


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


def esc(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def set_meta(head, pattern, value):
    new, n = re.subn(pattern, lambda m: m.group(1) + value.replace("&", "&amp;").replace('"', "&quot;") + m.group(2), head, count=1)
    if n != 1:
        raise SystemExit(f"meta not found: {pattern}")
    return new


def build(site, dates):
    src_path = os.path.join(ROOT, site["src"])
    src = open(src_path, encoding="utf-8").read()
    base, pages = site["base"], site["pages"]
    head = src[:src.index("</head>")]
    pre = src[src.index("</head>"):src.index("<main>") + len("<main>")]
    post = src[src.index("</main>"):]
    graph = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', head, re.S).group(1))["@graph"]
    website_node = next(n for n in graph if "WebSite" in types_of(n))
    website = website_node["@id"]
    person = next((n for n in graph if "Person" in types_of(n)), {})
    # every section page carries the entities its WebPage points to
    context_nodes = [
        {"@type": "WebSite", "@id": website, "url": website_node["url"], "name": website_node["name"],
         "publisher": {"@id": PERSON}},
        {"@type": "Person", "@id": PERSON, "name": "Naim Bin Hasan", "url": "https://naimbh.com/",
         "jobTitle": person.get("jobTitle"), "sameAs": person.get("sameAs", [])},
    ]

    # the home page's own last-changed date (whole file, ignoring the date field itself)
    home_url = base + "/"
    home_date = changed_on(dates, home_url, re.sub(r'"dateModified": "[^"]*"', "", src))
    fixed = re.sub(r'("@type": "ProfilePage",(?:(?!"@type").)*?"dateModified": ")[^"]*(")',
                   lambda m: m.group(1) + home_date + m.group(2), src, count=1, flags=re.S)
    if fixed != src:
        open(src_path, "w", encoding="utf-8").write(fixed)
        src = fixed
        head = src[:src.index("</head>")]

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
        chunks = [src.__getitem__(slice(*find_section(src, k))) for k in page["ids"]]
        page["date"] = changed_on(dates, url, json.dumps(page, sort_keys=True, default=str) + "".join(chunks))
        copied = [json.loads(json.dumps(node)) for node in graph
                  if set(types_of(node)) & set(page.get("jsonld", []))]
        webpage = {"@type": page.get("type", "WebPage"), "@id": url + "#webpage", "url": url,
                   "name": page["title"], "description": page["desc"], "inLanguage": "en",
                   "isPartOf": {"@id": website}, "about": {"@id": PERSON},
                   "breadcrumb": {"@id": url + "#breadcrumb"}, "dateModified": page["date"]}
        for node in copied:
            if "ImageGallery" in types_of(node):  # the gallery lives here now
                node["url"] = url
                webpage["mainEntity"] = {"@id": node["@id"]}
        ld = [
            webpage,
            {"@type": "BreadcrumbList", "@id": url + "#breadcrumb", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": site["home_name"], "item": base + "/"},
                {"@type": "ListItem", "position": 2, "name": page["label"], "item": url}]},
        ] + context_nodes + copied
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
        body = '\n\n<div class="rule"></div>\n\n'.join(chunks) if site["out"] == "" else "\n\n".join(chunks)
        if "gallery" in page["ids"]:  # first thumbnails are above the fold on this page
            seen = [0]
            def eager(m):
                seen[0] += 1
                if seen[0] > 6:
                    return m.group(0)
                tag = m.group(0).replace(' loading="lazy"', '')
                return tag.replace('<img ', '<img fetchpriority="high" ', 1) if seen[0] == 1 else tag
            body = re.sub(r'<img [^>]*/images/gallery/[^>]*>', eager, body)
        if "gallery" in page["ids"]:  # the photo viewer sits right after the gallery section
            body += "\n\n" + re.search(r'<dialog class="lb".*?</dialog>', src, re.S).group(0)
        # the page heading becomes the <h1>
        hm = re.search(site["heading"], body)
        close = body.index("</h2>", hm.start())
        h1_open = body.index(">", hm.start()) + 1
        h1_text = esc(page["h1"]) if page.get("h1") else body[h1_open:close]
        body = body[:hm.start()] + "<h1" + body[hm.start() + 3:h1_open] + h1_text + "</h1>" + body[close + 5:]
        if page.get("intro"):  # a short passage that only this page has
            end_h1 = body.index("</h1>", hm.start()) + len("</h1>")
            body = (body[:end_h1] + f'\n    <p class="{site["intro_class"]}">{esc(page["intro"])}</p>' + body[end_h1:])

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
        entries.append(f'  <url>\n    <loc>{base}/{page["slug"]}/</loc>\n    <lastmod>{page["date"]}</lastmod>{imgs}\n  </url>')
    block = "\n  <!-- section pages: tools/build_pages.py -->\n" + "\n".join(entries) + "\n  <!-- /section pages -->\n"
    sm = sm.replace("\n</urlset>", block + "</urlset>")
    sm = re.sub(r"(<loc>%s</loc>\s*<lastmod>)[^<]*(</lastmod>)" % re.escape(home_url),
                lambda m: m.group(1) + home_date + m.group(2), sm, count=1)
    open(path, "w", encoding="utf-8").write(sm)
    print("sitemap", site["sitemap"], len(pages), "pages")


if __name__ == "__main__":
    dates = load_dates()
    for s in SITES:
        build(s, dates)
    with open(DATES, "w", encoding="utf-8") as f:
        json.dump(dates, f, indent=1, sort_keys=True)
        f.write("\n")
