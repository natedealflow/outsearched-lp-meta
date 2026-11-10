#!/usr/bin/env python3
"""Builds the OutSearched ad landing pages.

  Google ads -> live.outsearched.com   (repo natedealflow/outsearched-lp-google)
  Meta ads   -> start.outsearched.com  (repo natedealflow/outsearched-lp-meta)

One template, two variants. The only differences are the tracking tag and the
Tally form ID. Run:  python3 build_lp.py
"""
import html, json, os, shutil
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = "/home/claude/ty/assets"
OUT = {"google": "/home/claude/outsearched-lp-google", "meta": "/home/claude/outsearched-lp-meta"}

# ------------------------------------------------------------------ config
CALENDLY_ADS = "https://calendly.com/nate-outsearched/strategy-call-with-outsearched-website-clone"
VARIANTS = {
    "google": {
        "domain": "live.outsearched.com",
        "tally_form": "q5arO9",    # Tally: OutSearched | Google Ads Application (blank = book straight on Calendly)
        "source": "google",
        "GOOGLE_ADS_ID": "AW-18161038602",
        "META_PIXEL_ID": "",
    },
    "meta": {
        "domain": "start.outsearched.com",
        "tally_form": "QoMZdG",    # Tally: OutSearched | Meta Ads Application
        "source": "meta",
        "GOOGLE_ADS_ID": "",
        "META_PIXEL_ID": "4211957752402802",
    },
}
TRUSTPILOT = "https://www.trustpilot.com/review/outsearched.com"
# GoHighLevel inbound webhook (OutSearched sub-account, workflow "Ad Landing Page Applications").
GHL_WEBHOOK = "https://services.leadconnectorhq.com/hooks/TjwkkpfaWQx9DJtweeOi/webhook-trigger/d24abc95-4786-4294-9ffd-19852c658873"
PRIVACY = "/privacy/"  # outsearched.com has no privacy page, so each landing site hosts its own
# Main video: self-hosted on Vercel (project outsearched-projects, repo natedealflow/outsearched-projects /videos).
# New cut = new filename (main-v2.mp4); files are cached for a year.
HERO_VIDEO = "https://outsearched-projects.vercel.app/videos/main-v1.mp4"
HERO_POSTER = "https://outsearched-projects.vercel.app/videos/main-v1-poster.jpg"
# Step videos: a Wistia media ID, or a self-hosted file on Vercel (same host and caching as the main video).
VID_STEPS = [
    {"src": "https://outsearched-projects.vercel.app/videos/step1-v1.mp4",
     "poster": "https://outsearched-projects.vercel.app/videos/step1-v1-poster.jpg",
     "label": "Step 1: how we define your mandate and build your list"},
    {"src": "https://outsearched-projects.vercel.app/videos/step2-v2.mp4",
     "poster": "https://outsearched-projects.vercel.app/videos/step2-v1-poster.jpg",
     "label": "Step 2: how we reach owners directly"},
    {"src": "https://outsearched-projects.vercel.app/videos/step3-v3.mp4",
     "poster": "https://outsearched-projects.vercel.app/videos/step3-v1-poster.jpg",
     "label": "Step 3: how we qualify owners, get financials and get you to LOI"},
]
WISTIA_STEPS = [m for m in VID_STEPS if isinstance(m, str)]


def step_player(m):
    if isinstance(m, str):
        return f'<wistia-player media-id="{m}" aspect="1.7777777777777777"></wistia-player>'
    return (f'<video src="{m["src"]}" poster="{m["poster"]}" controls playsinline preload="none" '
            f'aria-label="{e(m["label"])}"></video>')

# ------------------------------------------------------------------ content
# Verbatim excerpts from OutSearched's Trustpilot page (16 reviews, all 5 stars).
REVIEWS = [
    ("Hire Nate. Couldn't recommend more highly", "Nate has done an amazing job working his sourcing magic and generating introductions that have led to quality conversations.", "Phil", "Jul 2025"),
    ("Great experience!", "We are able to issue 3 LOIs within a few months of getting up and running.", "Stephen X.", "Mar 2026"),
    ("Quick to First Deal", "I have a deal (nearing LOI) on my plate already with less than 60 days of outbound.", "CJ Jacobs, The Edelweiss Company", "Feb 2026"),
    ("No Stone Unturned", "Within three weeks, we were in active conversations with attractive acquisition targets.", "John M.", "Feb 2026"),
    ("Highly Recommend for PE Rollups", "They were one of the only companies in the space that seemed to actually know what they were doing.", "Justin Abrams", "Feb 2026"),
    ("Great outbound capability", "Submitted an LOI on an actionable target in the first 60 days.", "Travis Monteleone", "Aug 2025"),
]

STATS = [
    ("$500M+", "in deals brought to clients"),
    ("21 days", "to a live deal team"),
    ("$300M+", "enterprise value sourced for one PE client"),
    ("16", "five-star reviews on Trustpilot"),
]

STEPS = [
    ("Define your mandate and build the list",
     "We lock in exactly what you can buy: size, geography, vertical and EBITDA. Then we build a custom list of owners who match your mandate.",
     "You only ever look at businesses that actually fit."),
    ("Reach owners directly",
     "We enrich the data, write the messaging and reach owners by email, phone and direct mail. No brokers, no auctions. We get in before the deal is listed.",
     "While everyone else fights over listed deals, you are already talking with the owner."),
    ("Qualify, get financials and get to LOI",
     "We take the first calls, screen the owners, get NDAs signed and pull the financials. You get a full report every week.",
     "When you find one you like, we help you negotiate to a signed LOI."),
]

BENEFITS = [
    ("Off-market deal flow", "We go direct to owners, so you see actionable deals before they reach the market. Skip the brokers and the auctions."),
    ("A deal team for less than one hire", "A dedicated analyst, proven systems, weekly reporting and a weekly strategy call, for a fraction of the cost of a single BD hire."),
    ("Your deal team live in 21 days", "We build your list, staff your team and start outreach within 21 days. Most clients are in qualified owner conversations within 60."),
    ("True buy-side advisory", "Outreach, qualification, NDAs, financials, weekly reports, strategy calls and negotiating the LOI. We handle all of it."),
    ("All of the market, not 40%", "Databases like Grata, Inven and CapIQ show about 40% of investable businesses. We build lists that cover the whole market, so you don't need another subscription."),
    ("Weekly reports and strategy calls", "A full pipeline report every Friday and a strategy call every Monday. You stay in the loop without doing the work."),
]

FAQS = [
    ("What exactly do you do?",
     "We're your outsourced deal team. We find, contact and qualify off-market business owners who match your exact buy box, and deliver them to you. We handle the data, the messaging, outreach by email, phone and direct mail, the qualification calls, the NDAs and the financials. You get weekly reports and a dedicated strategy call. You focus on closing."),
    ("How does this work?",
     "We start with a strategy call to define your mandate: size, geography, vertical and EBITDA. From there we build your target list, enrich the contact data, write the messaging and have your deal team live within 21 days. Every week you get a report of active deals and a strategy call to review the pipeline. When you find one you like, we help you negotiate to LOI."),
    ("What do I get when I work with you?",
     "A dedicated analyst. A custom target list. Enriched contact data. Outreach by email, phone and direct mail. Qualification calls handled for you. NDAs and financials pulled. A pipeline report every Friday and a strategy call every Monday. And a team that has done this for PE groups, family offices, independent sponsors and serious individual buyers across the US."),
    ("What are realistic expectations?",
     "Results depend on your mandate and market, but here is what we've seen. LP First Capital had 5 qualified deals and submitted an LOI in 60 days. Bill had 6 actionable deals in 60 days. Edenhall Capital delivered two LOIs in 90 days. We've sourced over $300M in enterprise value for Alpine Private Equity. Most clients are in qualified owner conversations within 60 days."),
    ("How is this different from hiring a business development rep?",
     "Hiring is slow, expensive and a gamble. You spend months searching, interviewing and onboarding, then hope they deliver. With OutSearched you get a proven team and proven systems, live in 21 days. No headcount and no training. You're not paying us to figure it out."),
    ("I've tried outreach before and it didn't work.",
     "Most outreach fails because it's patchwork: a few emails a day, inconsistent follow-up and no real system. We send thousands of touches across email, phone and direct mail, with messaging refined across dozens of mandates and hundreds of thousands of contacts. It's a full outreach engine built for buying businesses."),
    ("Is this just a database like Grata or Inven?",
     "No. Databases give you information. They don't find, contact or qualify owners for you, and they cover about 40% of the investable market. We build custom lists that cover all of it, enrich the data, and our team does the outreach and qualification. You get real conversations with owners who are ready to talk."),
    ("What if I have a tough or niche buy box?",
     "That's where we do our best work. The tougher the mandate, the more value we add. We've sourced deals in industrials at $19M EBITDA, home services at $1.4M EBITDA and everything in between, across the US."),
    ("How quickly can you get started?",
     "Your deal team is built and live within 21 days of your strategy call. Most clients are in qualified owner conversations within 60 days."),
]

# ------------------------------------------------------------------ assets
def make_assets(dst):
    a = os.path.join(dst, "assets")
    os.makedirs(a, exist_ok=True)
    shutil.copy(os.path.join(ASSETS, "logo-reversed.png"), os.path.join(a, "logo-reversed.png"))
    shutil.copy(os.path.join(ASSETS, "logo-primary.png"), os.path.join(a, "logo-primary.png"))
    # Favicon: the node mark cropped from the real primary logo file (no redrawing).
    prim = Image.open(os.path.join(ASSETS, "logo-primary.png")).convert("RGBA")
    mark = prim.crop((0, 0, 285, 270))
    mark = mark.crop(mark.getbbox())
    side = max(mark.size) + 24
    sq = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    sq.paste(mark, ((side - mark.width) // 2, (side - mark.height) // 2), mark)
    sq.resize((180, 180), Image.LANCZOS).save(os.path.join(a, "apple-touch-icon.png"))
    sq.resize((64, 64), Image.LANCZOS).save(os.path.join(a, "favicon.png"))
    # Social share image: real reversed logo on Midnight Navy.
    og = Image.new("RGB", (1200, 630), (0x2E, 0x40, 0x58))
    rev = Image.open(os.path.join(ASSETS, "logo-reversed.png")).convert("RGBA")
    rev = rev.crop(rev.getbbox())
    w = 820
    rev = rev.resize((w, int(rev.height * w / rev.width)), Image.LANCZOS)
    og.paste(rev, ((1200 - rev.width) // 2, (630 - rev.height) // 2 - 10), rev)
    bar = Image.new("RGB", (216, 6), (0xBD, 0xA2, 0x5B))
    og.paste(bar, (0, 624))
    og.save(os.path.join(a, "og.png"), optimize=True)


# ------------------------------------------------------------------ styles
CSS = r"""
:root{
  --navy:#2E4058; --navy-900:#16202E; --navy-800:#223247; --navy-100:#DCE2E9; --navy-050:#F2F5F8;
  --gold:#BDA25B; --gold-light:#D4BE85; --gold-deep:#8A7434;
  --sage:#76817B; --sage-deep:#5A6660; --graphite:#393A3C;
  --parchment:#F6F3EA; --parchment-line:#E8E3D6; --white:#FFFFFF;
  --f-display:"Source Serif 4", Cambria, Georgia, serif;
  --f-body:"Source Sans 3", Calibri, "Segoe UI", system-ui, sans-serif;
  --f-label:"Jost", "Futura", "Century Gothic", system-ui, sans-serif;
  --r:4px; --wrap:1120px;
  color-scheme: light;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth;scroll-padding-top:80px}
body{margin:0;background:var(--parchment);color:var(--navy-900);font:400 17px/1.6 var(--f-body);-webkit-font-smoothing:antialiased;overflow-x:hidden}
img{max-width:100%;display:block}
a{color:inherit}
.wrap{max-width:var(--wrap);margin:0 auto;padding-left:max(16px, env(safe-area-inset-left, 0px));padding-right:max(16px, env(safe-area-inset-right, 0px))}
h1,h2,h3{font-family:var(--f-display);font-weight:600;line-height:1.15;margin:0;text-wrap:balance;letter-spacing:-.01em}
h2{font-size:clamp(28px,3.6vw,40px);color:var(--navy)}
h3{font-size:21px;color:var(--navy)}
p{margin:0}
.eyebrow{font:500 13px/1.2 var(--f-label);letter-spacing:.16em;text-transform:uppercase}
.lede{font-size:19px;color:var(--sage-deep);max-width:62ch}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:10px;min-height:48px;padding:0 26px;border-radius:var(--r);
  background:var(--gold);color:var(--navy-900);font:600 14px/1 var(--f-label);letter-spacing:.12em;text-transform:uppercase;text-decoration:none;border:0;cursor:pointer;transition:background .15s}
.btn:hover{background:var(--gold-light)}
.btn:focus-visible,a:focus-visible,summary:focus-visible{outline:2px solid var(--gold);outline-offset:3px}
.btn.ghost{background:transparent;color:var(--white);box-shadow:inset 0 0 0 1px rgba(255,255,255,.35)}
.btn.ghost:hover{background:rgba(255,255,255,.08)}

/* header */
.top{position:sticky;top:0;z-index:20;background:rgba(46,64,88,.97);backdrop-filter:saturate(1.2) blur(6px);border-bottom:1px solid rgba(255,255,255,.08)}
.top .wrap{display:flex;align-items:center;justify-content:space-between;gap:16px;min-height:68px}
.top img{height:46px;width:auto}
.top .btn{min-height:42px;padding:0 18px;font-size:13px;white-space:nowrap}

/* hero */
.hero{background:var(--navy);color:var(--white);position:relative}
.hero::after{content:"";position:absolute;left:0;right:0;bottom:0;height:3px;background:linear-gradient(90deg,var(--gold) 0 18%,transparent 18%)}
.hero .wrap{display:grid;grid-template-columns:minmax(0,1.05fr) minmax(0,.95fr);gap:48px;align-items:start;padding-top:64px;padding-bottom:72px}
.hero p.eyebrow{color:var(--gold-light);display:flex;align-items:center;gap:12px}
.hero p.eyebrow::before{content:"";width:28px;height:1px;background:var(--gold)}
.hero h1{font-size:clamp(34px,4.6vw,54px);margin-top:18px;color:var(--white)}
.hero h1 .gold{color:var(--gold-light)}
.hero .sub{margin-top:20px;font-size:19px;line-height:1.55;color:var(--navy-100);max-width:52ch}
.hero .sub b{color:var(--white);font-weight:600}
.proof{margin-top:24px;display:flex;align-items:center;gap:12px;flex-wrap:wrap;font-size:15px;color:var(--navy-100)}
.proof .stars{color:var(--gold);letter-spacing:3px;font-size:18px}
.proof a{color:var(--white);text-underline-offset:3px}

/* form card */
.apply{background:var(--white);color:var(--navy-900);border-radius:var(--r);box-shadow:0 30px 60px -30px rgba(0,0,0,.55);overflow:hidden}
.apply-head{padding:18px 22px;border-bottom:1px solid var(--parchment-line);display:flex;justify-content:space-between;align-items:center;gap:12px}
.apply-head .eyebrow{color:var(--gold-deep);font-size:12px}
.apply-head span{font-size:14px;color:var(--sage-deep);white-space:nowrap}
.apply-head .eyebrow{white-space:nowrap}
.apply-body{padding:6px 10px 10px;min-height:420px}
.apply-body iframe{width:100%;border:0;display:block}
.apply-foot{background:var(--parchment);padding:12px 22px;font-size:13px;color:var(--sage-deep)}
.dq{display:none;padding:28px 14px 22px}
.dq.show{display:block}
.dq p{font-size:16px;line-height:1.6;color:var(--navy-900);margin:0 0 14px}
.dq .dq-title{font-family:var(--f-display);font-weight:600;font-size:26px;line-height:1.25;margin-bottom:16px}
.cal{display:none}
.cal.show{display:block}
.cal .cal-inline{min-width:280px;height:700px;position:relative}
.cal-loading{position:absolute;top:24px;left:0;right:0;text-align:center;font-size:15px;color:var(--sage-deep);margin:0}
.cal-inline iframe{position:relative;z-index:1;background:transparent}
.cal-note{padding:16px 14px 6px;font-size:15px;color:var(--navy)}

/* stats */
.stats{background:var(--navy-900);color:var(--white)}
.stats ul{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(4,minmax(0,1fr))}
.stats li{padding:30px 22px;border-left:1px solid rgba(255,255,255,.08)}
.stats li:first-child{border-left:0;padding-left:0}
.stats b{display:block;font:600 clamp(30px,3.4vw,40px)/1 var(--f-display);color:var(--gold-light);font-variant-numeric:tabular-nums}
.stats span{display:block;margin-top:10px;font-size:15px;color:var(--navy-100)}

/* bands */
.band{padding:84px 0}
.band.white{background:var(--white)}
.band.navy{background:var(--navy);color:var(--white)}
.band.navy h2{color:var(--white)}
.band-head{max-width:760px;margin-bottom:44px}
.band-head .eyebrow{color:var(--gold-deep);display:block;margin-bottom:14px}
.navy .band-head .eyebrow{color:var(--gold-light)}
.band-head .lede{margin-top:14px}
.navy .lede{color:var(--navy-100)}

/* video */
.video{position:relative;padding-top:56.25%;background:var(--navy-900);border-radius:var(--r);overflow:hidden;box-shadow:0 30px 60px -36px rgba(0,0,0,.6)}
.video wistia-player{position:absolute;inset:0;display:block}
.video video{position:absolute;inset:0;width:100%;height:100%;display:block;object-fit:cover;background:var(--navy-900)}
.video-wrap{max-width:900px}

/* steps */
.steps{display:grid;gap:56px}
.step{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:48px;align-items:center}
.step:nth-child(even) .step-text{order:2}
.step .num{font:600 13px/1 var(--f-label);letter-spacing:.16em;text-transform:uppercase;color:var(--gold-deep)}
.step h3{font-size:clamp(23px,2.4vw,28px);margin:12px 0 14px}
.step p{color:var(--sage-deep)}
.step p + p{margin-top:12px}
.step .pay{color:var(--navy);font-weight:600}

/* benefits */
.grid3{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:0;border-top:1px solid var(--parchment-line)}
.benefit{padding:30px 28px 30px 0;border-bottom:1px solid var(--parchment-line)}
.benefit:not(:nth-child(3n+1)){padding-left:28px;border-left:1px solid var(--parchment-line)}
.benefit h3{font-size:20px;margin-bottom:10px;display:flex;gap:12px;align-items:baseline}
.benefit h3::before{content:"";width:8px;height:8px;background:var(--gold);flex:none;transform:translateY(-3px)}
.benefit p{color:var(--sage-deep);font-size:16px}

/* reviews */
.score{display:flex;flex-wrap:wrap;align-items:center;gap:16px 32px;margin-bottom:36px}
.score .big{font:600 52px/1 var(--f-display);color:var(--navy)}
.score .stars{color:var(--gold);letter-spacing:3px;font-size:20px}
.score .meta{color:var(--sage-deep);font-size:15px}
.score a{color:var(--navy);font-weight:600;text-underline-offset:3px}
.reviews{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:20px}
.review{margin:0;background:var(--parchment);border-radius:var(--r);padding:24px;display:flex;flex-direction:column;gap:12px;min-width:0}
.review .stars{color:var(--gold);letter-spacing:2px;font-size:15px;line-height:1}
.review-title{font:600 16px/1.35 var(--f-body);color:var(--navy)}
.review blockquote{margin:0;font:400 19px/1.5 var(--f-display);color:var(--navy-900);flex:1}
.review figcaption{display:flex;flex-direction:column;gap:2px;padding-top:14px;border-top:1px solid var(--navy-100);font-weight:600;font-size:15px;color:var(--navy)}
.review figcaption .when{font-weight:400;font-size:13px;color:var(--sage-deep)}

/* faq */
.faq{max-width:820px;border-top:1px solid var(--parchment-line)}
.faq details{border-bottom:1px solid var(--parchment-line)}
.faq summary{list-style:none;cursor:pointer;padding:22px 44px 22px 0;position:relative;font:600 19px/1.4 var(--f-display);color:var(--navy)}
.faq summary::-webkit-details-marker{display:none}
.faq summary::after{content:"";position:absolute;right:6px;top:50%;width:12px;height:12px;border-right:2px solid var(--gold-deep);border-bottom:2px solid var(--gold-deep);transform:translateY(-70%) rotate(45deg);transition:transform .2s}
.faq details[open] summary::after{transform:translateY(-30%) rotate(-135deg)}
.faq details p{padding:0 0 24px;color:var(--sage-deep);max-width:70ch}

/* cta */
.cta{text-align:center}
.cta .wrap{max-width:760px}
.cta .lede{margin:16px auto 28px;color:var(--navy-100)}

/* footer */
footer{background:var(--navy-900);color:var(--navy-100);padding:44px 0 36px;font-size:14px}
footer .wrap{display:grid;gap:18px}
footer img{height:38px;width:auto}
footer .row{display:flex;flex-wrap:wrap;gap:8px 22px;align-items:center}
footer a{color:var(--white);text-underline-offset:3px}
footer .fine{font-size:12px;color:var(--sage);max-width:80ch}

@media (max-width: 900px){
  .hero .wrap{grid-template-columns:minmax(0,1fr);gap:32px;padding-top:40px;padding-bottom:56px}
  .stats ul{grid-template-columns:repeat(2,minmax(0,1fr))}
  .stats li{padding:22px 16px}
  .stats li:nth-child(odd){border-left:0;padding-left:0}
  .stats li:nth-child(n+3){border-top:1px solid rgba(255,255,255,.08)}
  .step{grid-template-columns:minmax(0,1fr);gap:22px}
  .step:nth-child(even) .step-text{order:0}
  .grid3,.reviews{grid-template-columns:minmax(0,1fr)}
  .benefit,.benefit:not(:nth-child(3n+1)){padding:24px 0;border-left:0}
  .band{padding:60px 0}
}
@media (max-width: 420px){
  .top img{height:36px}
  .apply-head{padding:16px}
  .apply-head span:last-child{font-size:13px}
  .top .btn{padding:0 14px;letter-spacing:.08em}
}
@media (prefers-reduced-motion: reduce){html{scroll-behavior:auto}*{transition:none!important}}
"""

FONTS = ('<link rel="preconnect" href="https://calendly.com"><link rel="preconnect" href="https://assets.calendly.com"><link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Jost:wght@500;600&family=Source+Sans+3:wght@400;600&family=Source+Serif+4:opsz,wght@8..60,500;8..60,600&display=swap">')

e = html.escape


def tracking_head(v):
    out = []
    if v["GOOGLE_ADS_ID"]:
        gid = v["GOOGLE_ADS_ID"]
        out.append(f"""<script async src="https://www.googletagmanager.com/gtag/js?id={gid}"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','{gid}');</script>""")
    if v["META_PIXEL_ID"]:
        pid = v["META_PIXEL_ID"]
        out.append(f"""<script>!function(f,b,e,v,n,t,s){{if(f.fbq)return;n=f.fbq=function(){{n.callMethod?n.callMethod.apply(n,arguments):n.queue.push(arguments)}};if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}}(window,document,'script','https://connect.facebook.net/en_US/fbevents.js');fbq('init','{pid}');fbq('track','PageView');</script>
<noscript><img height="1" width="1" style="display:none" alt="" src="https://www.facebook.com/tr?id={pid}&ev=PageView&noscript=1"></noscript>""")
    return "\n".join(out)


def form_block(v):
    tally = v["tally_form"]
    if tally:
        form = (f'<iframe data-tally-src="https://tally.so/embed/{tally}?hideTitle=1&transparentBackground=1&dynamicHeight=1&source={v["source"]}" '
                'width="100%" height="420" title="See if you qualify"></iframe>')
        cal_cls = "cal"
    else:
        form = ""
        cal_cls = "cal show"
    return f"""
      <div class="apply" id="apply">
        <div class="apply-head"><span class="eyebrow">See if you qualify</span><span>Takes about 60 seconds</span></div>
        <div class="apply-body">
          {form}
          <div class="dq" id="dq">
            <p class="dq-title" id="dq-title">Thanks for applying.</p>
            <p>Based on your answers, a strategy call isn't the right next step yet. Our clients are ready to start a search within 60 days, with at least $250K in liquid capital and $5,000 a month for deal flow.</p>
            <p>When your timing or budget changes, apply again and we'll pick it up from there.</p>
          </div>
          <div class="{cal_cls}" id="cal">
            <p class="cal-note" id="cal-note">Pick a time for your free strategy call with Nate.</p>
            <div class="cal-inline" id="cal-widget" data-base="{CALENDLY_ADS}"><p class="cal-loading">Loading available times...</p></div>
          </div>
        </div>
        <div class="apply-foot">Your information stays private. We never share it.</div>
      </div>"""


def page(v):
    stats = "".join(f"<li><b>{e(a)}</b><span>{e(b)}</span></li>" for a, b in STATS)
    steps = "".join(f"""
      <div class="step">
        <div class="step-text">
          <span class="num">Step {i+1} of 3</span>
          <h3>{e(t)}</h3>
          <p>{e(d)}</p>
          <p class="pay">{e(p)}</p>
        </div>
        <div class="video">{step_player(VID_STEPS[i])}</div>
      </div>""" for i, (t, d, p) in enumerate(STEPS))
    benefits = "".join(f'<div class="benefit"><h3>{e(t)}</h3><p>{e(d)}</p></div>' for t, d in BENEFITS)
    reviews = "".join(f"""
        <figure class="review">
          <div class="stars" aria-label="5 out of 5 stars">&#9733;&#9733;&#9733;&#9733;&#9733;</div>
          <p class="review-title">{e(t)}</p>
          <blockquote>&ldquo;{e(q)}&rdquo;</blockquote>
          <figcaption><span>{e(w)}</span><span class="when">{e(d)} &middot; Trustpilot</span></figcaption>
        </figure>""" for t, q, w, d in REVIEWS)
    faqs = "".join(f"<details><summary>{e(q)}</summary><p>{e(a)}</p></details>" for q, a in FAQS)
    cfg = json.dumps({"source": v["source"], "googleAds": v["GOOGLE_ADS_ID"], "metaPixel": v["META_PIXEL_ID"], "tally": v["tally_form"], "ghl": GHL_WEBHOOK})
    tally_script = ('<script>(function(){'
                    'document.querySelectorAll("iframe[data-tally-src]").forEach(function(fr){'
                    'var u=new URL(fr.getAttribute("data-tally-src"));'
                    'new URLSearchParams(location.search).forEach(function(v,k){if(!u.searchParams.has(k))u.searchParams.set(k,v);});'
                    'u.searchParams.set("originPage",location.pathname);fr.src=u.toString();});'
                    'var s=document.createElement("script");s.src="https://tally.so/widgets/embed.js";s.async=true;document.body.appendChild(s);'
                    '})();</script>') if v["tally_form"] else ""
    url = f"https://{v['domain']}/"
    desc = "We find, contact and qualify off-market business owners that match your exact buy box. Your deal team is live in 21 days."
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>OutSearched | Off-market deal sourcing for serious business buyers</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:url" content="{url}">
<meta property="og:title" content="The best businesses sell before they're listed">
<meta property="og:description" content="{e(desc)}">
<meta property="og:image" content="{url}assets/og.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#2E4058">
<link rel="icon" type="image/png" href="/assets/favicon.png">
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
{FONTS}
<style>{CSS}</style>
{tracking_head(v)}
</head>
<body>
<header class="top">
  <div class="wrap">
    <img src="/assets/logo-reversed.png" alt="OutSearched, Origination &amp; Advisory" width="900" height="271">
    <a class="btn" href="#apply">Book a call</a>
  </div>
</header>

<main>
<section class="hero">
  <div class="wrap">
    <div>
      <p class="eyebrow">Serious about buying a business?</p>
      <h1>The best businesses sell before they're listed. <span class="gold">We get them to you first.</span></h1>
      <p class="sub"><b>Over $500M in off-market deals sourced.</b> We find, contact and qualify off-market business owners who match your exact buy box. No brokers, no auctions, no wasted time.</p>
      <p class="proof"><span class="stars" aria-hidden="true">&#9733;&#9733;&#9733;&#9733;&#9733;</span><span>16 five-star reviews on <a href="{TRUSTPILOT}" target="_blank" rel="noopener">Trustpilot</a></span></p>
    </div>
    {form_block(v)}
  </div>
</section>

<section class="stats" aria-label="Results">
  <div class="wrap"><ul>{stats}</ul></div>
</section>

<section class="band white">
  <div class="wrap">
    <div class="band-head">
      <span class="eyebrow">Watch how it works</span>
      <h2>How we build an off-market deal engine around your buy box</h2>
      <p class="lede">90 seconds on how we build and staff your deal team.</p>
    </div>
    <div class="video-wrap"><div class="video"><video src="{HERO_VIDEO}" poster="{HERO_POSTER}" controls playsinline preload="metadata" aria-label="How OutSearched builds your off-market deal pipeline"></video></div></div>
  </div>
</section>

<section class="band">
  <div class="wrap">
    <div class="band-head">
      <span class="eyebrow">The process</span>
      <h2>We find, contact and qualify off-market owners, so you can focus on closing</h2>
    </div>
    <div class="steps">{steps}</div>
  </div>
</section>

<section class="band white">
  <div class="wrap">
    <div class="band-head">
      <span class="eyebrow">What you get</span>
      <h2>Everything a deal team does, without the hire</h2>
    </div>
    <div class="grid3">{benefits}</div>
    <p style="margin-top:36px"><a class="btn" href="#apply">See if you qualify</a></p>
  </div>
</section>

<section class="band">
  <div class="wrap">
    <div class="band-head">
      <span class="eyebrow">Client reviews</span>
      <h2>What our clients say</h2>
    </div>
    <div class="score">
      <span class="big">16</span>
      <div><div class="stars" aria-label="Five stars">&#9733;&#9733;&#9733;&#9733;&#9733;</div>
      <p class="meta">Five-star reviews on Trustpilot. <a href="{TRUSTPILOT}" target="_blank" rel="noopener">Read them on Trustpilot</a></p></div>
    </div>
    <div class="reviews">{reviews}</div>
  </div>
</section>

<section class="band white">
  <div class="wrap">
    <div class="band-head">
      <span class="eyebrow">FAQ</span>
      <h2>Questions buyers ask before the call</h2>
    </div>
    <div class="faq">{faqs}</div>
  </div>
</section>

<section class="band navy cta">
  <div class="wrap">
    <h2>Ready to stop waiting on brokers?</h2>
    <p class="lede">Book a free strategy call. We'll define your mandate and show you what your pipeline could look like in your first 60 days.</p>
    <a class="btn" href="#apply">See if you qualify</a>
  </div>
</section>
</main>

<footer>
  <div class="wrap">
    <img src="/assets/logo-reversed.png" alt="OutSearched" width="900" height="271" loading="lazy">
    <div class="row"><span>&copy; 2026 OutSearched, LLC</span><span>Austin, TX</span><a href="{PRIVACY}">Privacy policy</a><a href="https://outsearched.com/">outsearched.com</a></div>
    <p class="fine">This site is not part of the Google or Meta Platforms, Inc. websites and is not endorsed by Google or Meta in any way. All trademarks belong to their respective owners.</p>
  </div>
</footer>

<script>var OS_CFG={cfg};</script>
<script>
(function(cfg){{
  var params = new URLSearchParams(location.search);
  var keep = ["utm_source","utm_medium","utm_campaign","utm_content","utm_term"];
  function track(){{
    try{{ if(cfg.googleAds && window.gtag) gtag('event','generate_lead'); }}catch(e){{}}
    try{{ if(cfg.metaPixel && window.fbq) fbq('track','Lead'); }}catch(e){{}}
  }}
  var loaded = false;
  function showCalendly(name, email, note, extra){{
    var box = document.getElementById('cal'); box.classList.add('show');
    if(note) document.getElementById('cal-note').textContent = note;
    if(loaded) return; loaded = true;
    var w = document.getElementById('cal-widget');
    var u = new URL(w.getAttribute('data-base'));
    u.searchParams.set('hide_gdpr_banner','1');
    u.searchParams.set('primary_color','bda25b');
    if(name) u.searchParams.set('name', name);
    if(email) u.searchParams.set('email', email);
    // Calendly questions 1 and 2 ask the $5K question and cell phone again. Pre-answer them from the form.
    if(extra && extra.budget === 'Yes') u.searchParams.set('a1', 'Yes');
    if(extra && extra.phone){{ var dg = String(extra.phone).replace(/\\D/g,''); if(dg.length===10) dg='1'+dg; if(dg.length>=11) u.searchParams.set('a2', '+'+dg); }}
    keep.forEach(function(k){{ if(params.get(k)) u.searchParams.set(k, params.get(k)); }});
    if(!params.get('utm_term') && params.get('utm_keyword')) u.searchParams.set('utm_term', params.get('utm_keyword'));
    if(!params.get('utm_source')) u.searchParams.set('utm_source', cfg.source);
    var url = u.toString().replace(/\\+/g, '%20');
    w.setAttribute('data-url', url);
    // widget.js is loaded in the background when the page opens, so the calendar appears fast.
    (function go(n){{ if(window.Calendly && Calendly.initInlineWidget){{ Calendly.initInlineWidget({{url: url, parentElement: w}}); }} else if(n < 100){{ setTimeout(function(){{ go(n+1); }}, 100); }} }})(0);
  }}
  // When the Tally form is submitted, qualified applicants get the Calendly ads event right here. Its redirect opens /confirmed/.
  window.addEventListener('message', function(ev){{
    var d = ev.data;
    if(typeof d === 'string'){{ try{{ d = JSON.parse(d); }}catch(e){{ return; }} }}
    if(!d || d.event !== 'Tally.FormSubmitted' || !d.payload) return;
    try{{ console.log('[OS] tally payload', JSON.stringify(d.payload).slice(0,2000)); }}catch(e){{}}
    var f = d.payload.fields || [], ans = {{}};
    function text(x){{
      var v = x.answer && x.answer.value !== undefined ? x.answer.value : (x.value !== undefined ? x.value : x.answer);
      var opts = x.options || (x.answer && x.answer.options) || [];
      var map = function(o){{
        if(o && typeof o === 'object') return o.text || o.label || o.value || '';
        for(var i=0;i<opts.length;i++){{ if(opts[i].id === o) return opts[i].text; }}
        return o;
      }};
      if(Array.isArray(v)) v = v.map(map).join(', ');
      else v = map(v);
      return (v === undefined || v === null) ? '' : String(v);
    }}
    f.forEach(function(x){{
      var t = (x.title||x.label||'').toLowerCase(), val = text(x);
      if(t.indexOf('your name') > -1) ans.name = val;
      else if(t.indexOf('email') > -1) ans.email = val;
      else if(t.indexOf('phone') > -1) ans.phone = val;
      else if(t.indexOf('begin your search') > -1) ans.timeline = val;
      else if(t.indexOf('liquid capital') > -1) ans.capital = val;
      else if(t.indexOf('5,000') > -1) ans.budget = val;
      else if(t.indexOf('9 months') > -1) ans.months = val;
    }});
    track();
    var dq = /curious/i.test(ans.timeline||'') || /less than|<|under/i.test(ans.capital||'') || /^no$/i.test(ans.budget||'') || /^no$/i.test(ans.months||'');
    try{{ console.log('[OS] tally answers', JSON.stringify(ans), 'qualified', !dq); }}catch(e){{}}
    // Send the application to GoHighLevel (workflow: Ad Landing Page Applications).
    var label = cfg.source === 'meta' ? 'Meta ads (start.outsearched.com)' : 'Google ads (live.outsearched.com)';
    var rec = {{
      source: cfg.source, tags: cfg.source + ' lead, tally application' + (dq ? ', not qualified' : ''),
      full_name: ans.name||'', email: ans.email||'', phone: ans.phone||'',
      timeline: ans.timeline||'', liquid_capital: ans.capital||'', five_k_per_month: ans.budget||'', nine_months: ans.months||'',
      qualified: dq ? 'no' : 'yes',
      summary: 'Source: ' + label + ' | Timeline: ' + (ans.timeline||'') + ' | Liquid capital: ' + (ans.capital||'') + ' | $5K per month: ' + (ans.budget||'') + ' | 9 months: ' + (ans.months||'') + ' | Qualified: ' + (dq ? 'no' : 'yes') + ' | Campaign: ' + (params.get('utm_campaign')||''),
      utm_source: params.get('utm_source')||'', utm_medium: params.get('utm_medium')||'', utm_campaign: params.get('utm_campaign')||'',
      utm_content: params.get('utm_content')||'', utm_term: params.get('utm_term')||params.get('utm_keyword')||'',
      gclid: params.get('gclid')||'', fbclid: params.get('fbclid')||'', page: location.href.split('#')[0],
      form_id: cfg.tally, submission_id: d.payload.responseId || d.payload.id || ''
    }};
    try{{ fetch(cfg.ghl, {{method:'POST', headers:{{'content-type':'application/json'}}, body: JSON.stringify(rec), keepalive:true}}); }}catch(e){{}}
    var fr = document.querySelector('#apply iframe[data-tally-src]'); if(fr) fr.style.display = 'none';
    if(dq){{
      // Not a fit right now: show our own message instead of Tally's generic thank-you screen.
      var first = String(ans.name||'').trim().split(/\s+/)[0];
      document.getElementById('dq-title').textContent = first ? ('Thanks for applying, ' + first + '.') : 'Thanks for applying.';
      document.getElementById('dq').classList.add('show');
      document.getElementById('apply').scrollIntoView({{behavior:'smooth', block:'start'}});
    }}
    if(!dq){{
      showCalendly(ans.name, ans.email, 'You qualify. Pick a time for your free strategy call with Nate.', ans);
      document.getElementById('apply').scrollIntoView({{behavior:'smooth', block:'start'}});
    }}
  }});
  if(!cfg.tally) showCalendly('', '', '');
}})(OS_CFG);
</script>
{tally_script}
<script src="https://assets.calendly.com/assets/external/widget.js" async></script>
{'<script src="https://fast.wistia.com/player.js" async></script>' if WISTIA_STEPS else ''}
{''.join(f'<script src="https://fast.wistia.com/embed/{m}.js" async type="module"></script>' for m in WISTIA_STEPS)}
</body>
</html>
"""


PRIVACY_SECTIONS = [
    ("Who we are",
     ["OutSearched, LLC (\"OutSearched\", \"we\") is a buy-side M&A deal origination firm based in Austin, TX. This policy covers this website and the application form on it."]),
    ("What we collect",
     ["When you apply, we collect what you enter: your name, email, phone number and your answers about timing, capital and budget.",
      "When you book a call, our scheduling provider collects the details you enter there, such as your name, email, phone and answers to its questions.",
      "When you visit, we and our advertising partners collect standard technical information through cookies and similar tools, such as pages viewed, the ad or link that brought you here (including campaign tags and click IDs), browser and device type, and approximate location from your IP address."]),
    ("How we use it",
     ["To review your application, contact you about it, schedule and hold your strategy call, and follow up with you by email, phone or text about our services.",
      "To measure and improve our advertising and this website, including telling Google and Meta when someone applies or books a call so we can see which ads work."]),
    ("Who we share it with",
     ["We do not sell your personal information. We share it only with service providers that help us run this process: Tally (application form), Calendly (scheduling), GoHighLevel (our customer relationship system), Wistia and Vercel (video), Google (Google Ads and Google Fonts), Meta (the Meta Pixel) and GitHub (website hosting). Each handles your information under its own privacy terms.",
      "We may also share information if the law requires it, or as part of a sale or reorganization of our business."]),
    ("Cookies and ad tracking",
     ["This site uses the Google Ads tag and the Meta Pixel to measure ad results. You can block or delete cookies in your browser settings, opt out of personalized Google ads at adssettings.google.com, and manage Meta ad preferences in your Facebook or Instagram settings."]),
    ("Texts and calls",
     ["If you give us your phone number, we may call or text you about your application and your call. Message and data rates may apply. Reply STOP to any text to opt out."]),
    ("How long we keep it",
     ["We keep your information for as long as we need it for the purposes above or as required by law, then delete it."]),
    ("Your choices",
     ["You can ask us to access, correct or delete your personal information, or to stop contacting you, by emailing nate@outsearched.com. Depending on where you live, you may have additional rights under state law, and we will honor them."]),
    ("Security",
     ["We use reasonable measures to protect your information, but no method of sending or storing data is completely secure."]),
    ("Changes and contact",
     ["We may update this policy from time to time and will post the new version on this page. Questions: nate@outsearched.com, OutSearched, LLC, Austin, TX."]),
]


def privacy_page(v):
    url = f"https://{v['domain']}/privacy/"
    body = "".join(f"<h2>{e(h)}</h2>" + "".join(f"<p>{e(x)}</p>" for x in ps) for h, ps in PRIVACY_SECTIONS)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Privacy policy | OutSearched</title>
<meta name="description" content="How OutSearched collects and uses information on this website.">
<link rel="canonical" href="{url}">
<meta name="theme-color" content="#2E4058">
<link rel="icon" type="image/png" href="/assets/favicon.png">
{FONTS}
<style>{CSS}
.legal{{background:var(--white);padding:64px 0 80px}}
.legal .wrap{{max-width:760px}}
.legal h1{{font-size:clamp(32px,4vw,44px);margin:0 0 8px;color:var(--navy-900)}}
.legal .upd{{color:var(--sage-deep);margin:0 0 32px}}
.legal h2{{font-size:22px;margin:32px 0 10px;color:var(--navy-900)}}
.legal p{{color:var(--graphite);line-height:1.65;margin:0 0 12px}}
</style>
</head>
<body>
<header class="top">
  <div class="wrap">
    <a href="/"><img src="/assets/logo-reversed.png" alt="OutSearched, Origination &amp; Advisory" width="900" height="271"></a>
    <a class="btn" href="/#apply">Book a call</a>
  </div>
</header>
<main class="legal">
  <div class="wrap">
    <h1>Privacy policy</h1>
    <p class="upd">Last updated November 9, 2026</p>
    {body}
  </div>
</main>
<footer>
  <div class="wrap">
    <img src="/assets/logo-reversed.png" alt="OutSearched" width="900" height="271" loading="lazy">
    <div class="row"><span>&copy; 2026 OutSearched, LLC</span><span>Austin, TX</span><a href="/privacy/">Privacy policy</a><a href="https://outsearched.com/">outsearched.com</a></div>
  </div>
</footer>
</body>
</html>"""


if __name__ == "__main__":
    for key, v in VARIANTS.items():
        dst = OUT[key]
        if os.path.isdir(ASSETS):  # source logos only exist in the original build workspace; repos already hold the outputs
            make_assets(dst)
        with open(os.path.join(dst, "index.html"), "w") as f:
            f.write(page(v))
        with open(os.path.join(dst, "CNAME"), "w") as f:
            f.write(v["domain"] + "\n")
        open(os.path.join(dst, ".nojekyll"), "w").close()
        # Old ad links: Meta ads point at /schedule (and older /confirm pages). Serve the same page there.
        os.makedirs(os.path.join(dst, "privacy"), exist_ok=True)
        with open(os.path.join(dst, "privacy", "index.html"), "w") as f:
            f.write(privacy_page(v))
        for sub in ["schedule"]:
            os.makedirs(os.path.join(dst, sub), exist_ok=True)
            with open(os.path.join(dst, sub, "index.html"), "w") as f:
                f.write(page(v))
        # Any other unknown path: send the visitor to the home page, keeping the ad's tracking parameters.
        with open(os.path.join(dst, "404.html"), "w") as f:
            f.write('<!doctype html><meta charset="utf-8"><title>OutSearched</title><meta name="robots" content="noindex">'
                    '<script>location.replace("/"+location.search+location.hash)</script>'
                    '<a href="/">Continue to OutSearched</a>')
        shutil.copy(os.path.abspath(__file__), os.path.join(dst, "build_lp.py"))
        print("built", key, "->", dst)
