# -*- coding: utf-8 -*-
import io, re

SF='https://siliconflorist.com'
YT='https://youtube.com/@turoczy_'
SS='https://www.slideshare.net/turoczy'

GROUPS = [
("talk", "Keynotes, conference talks, and panels", [
 ("2018","Columbia GSAPP &mdash; &ldquo;Labs, Incubators, Colonies: Propeller and PIE,&rdquo; a duet with Andrea Chen of Propeller, New Orleans. Wood Auditorium, cohosted with NEW INC.","https://www.youtube.com/watch?v=_kDXQk9p314"),
 ("2018","TEDxPortland &mdash; &ldquo;An Introvert&rsquo;s Guide to Networking,&rdquo; Keller Auditorium, 3,000+ people","https://www.youtube.com/watch?v=Cj98mr_wUA0"),
 ("2013","HubSpot INBOUND, Boston &mdash; &ldquo;The Power of Humility,&rdquo; Bold Talks track","https://www.youtube.com/watch?v=Cs7Hr_CN5v4"),
 ("2020","Skoll World Forum &mdash; &ldquo;Ecosystem Builders as Second Responders to Crisis&rdquo;","https://socialventurers.com/ecosystem-builders-as-second-responders-to-crisis/"),
 ("2018","Kauffman Foundation ESHIP Summit, Kansas City &mdash; &ldquo;Why do you do what you do?&rdquo;","https://www.youtube.com/watch?v=VsnNX2vPJM8"),
 ("recurring","SXSW Interactive, Austin &mdash; SXSW Pitch judge and advisory board, and curator of the Portland Tech Meet Up",""),
 ("2013","PSU Elevating Impact Summit &mdash; moderator, &ldquo;Resilience: Uncensored&rdquo;","https://www.pdx.edu/business/elevating-impact-2013"),
 ("2024","Silicon Forest Tech Summit &mdash; introducing the inaugural summit","https://www.youtube.com/watch?v=i3uXRPMEcGs"),
 ("2015","Whitman College &mdash; Andjelkovic Endowed Lecture Series, back at the alma mater","https://www.youtube.com/watch?v=5eyIqdpG4ZU"),
 ("2015","New Relic FutureTalk &mdash; moderating &ldquo;Mobile Strategy for Today and Tomorrow&rdquo;","https://www.youtube.com/watch?v=6S7t-vYhWYk"),
 ("2012","SOBCon, Chicago &mdash; on building things people actually show up for","https://www.youtube.com/watch?v=s5e0sH3POlw"),
 ("2009","InnoTech Conference &mdash; &ldquo;To Blog Or Not to Blog&rdquo;","https://www.slideshare.net/slideshow/20090422innotechblogornot/1361308"),
 ("archival","OEN PubTalk, Portland &mdash; &ldquo;The Tech Startup Scene in Portland&rdquo;",""),
 ("2026","PubTalks Fireside Chat, Eugene &mdash; two decades of Oregon startups","https://www.tickettailor.com/events/collaborativeedo/2023310"),
 ("2025","FOSSY &mdash; &ldquo;Cooking Up Community: Build the Fire, Embrace Every Ingredient, Always Stir the Pot&rdquo;","https://2025.fossy.us/speaker/profile/486/index.html"),
 ("2008&ndash;09","PDX Web Innovators &mdash; Portland tech community retrospective and outlook","https://www.slideshare.net/slideshow/2008-portland-tech-recap-presentation/816775"),
 ("multiple","Kobe, Japan &mdash; invited keynote on regional ecosystem development",""),
 ("multiple","Muscat, Oman &mdash; invited keynote on building on local assets instead of cloning Silicon Valley",""),
]),
("show", "Shows I host", [
 ("2023&ndash;","<i>Portland, Oregon, Startup News</i> &mdash; weekly companion to Silicon Florist. Apple Podcasts, Spotify, Libsyn, YouTube","https://podcasts.apple.com/us/podcast/portland-oregon-startup-news-silicon-florist/id1711294699"),
 ("2024&ndash;","<i>Startup Stories with Silicon Florist</i> &mdash; long-form founder interviews across Oregon and SW Washington","https://podcasts.apple.com/us/podcast/startup-stories-with-silicon-florist/id1849468494"),
 ("2024&ndash;","<i>The Long Con</i> &mdash; in person only, no video calls, no format","https://podcasts.apple.com/us/podcast/the-long-con-with-rick-turoczy/id1810923457"),
 ("2023&ndash;","<i>Mildly Interesting People</i> &mdash; co-creator and co-host, with Cami Kaos","https://mildlyinterestingpeople.com/"),
 ("2020&ndash;21","<i>PIE Crowdcast</i> &mdash; live AMA series for founders during the pandemic","https://www.crowdcast.io/piepdx"),
 ("2009&ndash;11","<i>memePDX</i> &mdash; co-host with Cami Kaos. Episodes live in the Silicon Florist archive.","https://siliconflorist.com/2010/02/25/memepdx-026-jive-software-ceo-dawn-foster-joins-meego-open-source-bridge-yahoo-twitter-ngmoco-raises-25-million/"),
]),
("pod", "Podcasts and broadcasts, as a guest", [
 ("2023","<i>PDX Executive Podcast</i>, Dan Bruton &mdash; &ldquo;Rick Returns,&rdquo; on 15 years of PIE and Built Oregon","https://podcasts.apple.com/us/podcast/rick-returns-pie-built-oregon-co-founder-on-15-years/id1247188542?i=1000598535227"),
 ("2021","<i>PDX Executive Podcast</i>, Dan Bruton &mdash; building startup ecosystems and the evolution of tech community organizers","https://podcasts.apple.com/us/podcast/rick-turoczy-on-building-startup-ecosystems-and/id1247188542?i=1000532280101"),
 ("2017","<i>PR Talk</i>, Veracity Agency &mdash; &ldquo;Our Own Slice of PIE&rdquo;, on the PIE Cookbook and accelerating failure","https://www.veracityagency.com/podcast/rick-turoczy/"),
 ("2026","<i>My Open Source Experience</i> &mdash; the secrets to successful and sustainable events","https://www.youtube.com/watch?v=2h9yurfW0es"),
 ("2026","<i>Next Round VC</i> &mdash; the truth about startup accelerators","https://www.youtube.com/watch?v=IkeX3OZjfG4"),
 ("2025","Paden Squires &mdash; &ldquo;Grow Slow, Win Big: The Truth About the Compounding Effect&rdquo;","https://www.youtube.com/watch?v=sNQekLBGoZc"),
 ("2025","<i>FutureProof Business</i> &mdash; 30 years in startups: startup myths, VC truths, and building the Portland ecosystem","https://www.youtube.com/watch?v=WosfYTTAV8o"),
 ("2025","<i>The 5 Min Startup</i> &mdash; Episode 3, on why new businesses fail fast","https://www.youtube.com/watch?v=pbbAT6TcH-8"),
 ("2021","<i>The Communities Show</i>, Gamedev Camp &mdash; PIE, Built Oregon, TechfestNW, and the Portland startup community","https://www.youtube.com/watch?v=EIyNkXUrfY8"),
 ("2020","<i>Float Small Business</i> &mdash; Episode 6","https://www.youtube.com/watch?v=wKnK2BmHMwo"),
 ("2020","Millwork Commons &mdash; on the Portland startup community","https://www.youtube.com/watch?v=aVCeDXnT0nI"),
 ("2020","<i>Willamette Week</i> &mdash; Distant Voices, an early-pandemic conversation","https://www.youtube.com/watch?v=lG-ObTekUo0"),
 ("2017","The Tech Academy &mdash; Tech Talk","https://www.youtube.com/watch?v=0jsOaMwchew"),
 ("2015","<i>Launch Yourself</i>, Melissa Anzman &mdash; Session 28, on interacting more creatively","https://launchyourself.co/session28/"),
 ("2011","<i>GeekWire Radio</i>, John Cook &amp; Todd Bishop &mdash; sizing up the Seattle and Portland tech scenes","https://www.geekwire.com/2011/rewind-comparing-portland-seattle-tech-startup-scenes/"),
 ("2012","<i>GeekWire</i> &mdash; &ldquo;Four minutes on the train with&hellip; Portland startup guru Rick Turoczy of PIE&rdquo;","https://www.geekwire.com/2012/minutes-train-rick-turoczy/"),
 ("2020","<i>The Digital Native</i> &mdash; Episode 11, on PIE and structural incubator design","https://www.youtube.com/watch?v=bw2XY1gr3uM"),
 ("2025","<i>Startup Success</i>, Burkland &mdash; strategies for startups outside Silicon Valley","https://burklandassociates.com/podcasts/strategies-for-startups-outside-silicon-valley/"),
 ("2026","<i>The Intersection</i>, Intersectional Group &mdash; on founders socializing their concepts, blogging, curiosity, and abundance","https://www.iheart.com/podcast/269-the-intersection-presented-102288352/episode/its-really-important-for-founders-to-socialize-those-business-concepts-with-rick-turoczy-on-portlands-startup-community-blogging-long-live-silicon-florist-curiosity-and-abundance-318624657"),
 ("2018","<i>And Uhhh</i> &mdash; Episode 4","https://podcasts.apple.com/us/podcast/episode-4-rick-turoczy/id1347311606?i=1000412586971"),
 ("2025","<i>Overcommitted</i> &mdash; &ldquo;Navigating the Startup Landscape,&rdquo; on founder burnout and where startups actually fail","https://podcasts.apple.com/us/podcast/navigating-the-startup-landscape-with-rick-turoczy/id1804549260?i=1000735230674"),
 ("archival","<i>PushPull</i> &mdash; Episode 17, &ldquo;Startin&rsquo; Stuff&rdquo;","https://pushpull.me/episode/episode-17-startin-stuff"),
 ("2022","<i>Social Venturers</i> &mdash; S04E08, &ldquo;Succession Planning: Transferring Social Capital to the Next Generation&rdquo;","https://socialventurers.com/s04e08/"),
]),
("press", "Press and mentions", [
 ("2008","<i>The Oregonian</i> &mdash; Steve Woodward on Portland&rsquo;s early Twitter adoption","https://web.archive.org/web/20160315014332/http://www.oregonlive.com/special/index.ssf/2008/05/twitter_is_tweeter.html"),
 ("2009","PBS <i>The NewsHour with Jim Lehrer</i> &mdash; &ldquo;Tech Industry Faces Struggles Amid Economic Slump.&rdquo; Lee Hochberg reporting from Portland; I turn up on the chyron as a high-tech industry analyst, which was news to me.","https://web.archive.org/web/20090203074541/http://www.pbs.org:80/newshour/bb/business/jan-june09/techindustry_01-22.html"),
 ("2010","OregonLive / <i>The Oregonian</i> &mdash; &ldquo;30 Hour Day brings the telethon into the digital age&rdquo;","https://web.archive.org/web/20160310122439/http://www.oregonlive.com/entertainment/index.ssf/2010/06/30_hour_day_brings_the_teletho.html"),
 ("2011","<i>The Oregonian</i> &mdash; Mike Rogoway on the launch of PIE",""),
 ("2011","<i>GeekWire</i> &mdash; &ldquo;Google tosses support behind the Portland Incubator Experiment&rdquo;","https://www.geekwire.com/2011/google-tosses-support-portland-incubator-experiment/"),
 ("2011","<i>GeekWire</i> &mdash; &ldquo;Startup incubator reheats in Portland with help from Coke, Nike and Target&rdquo;","https://www.geekwire.com/2011/startup-tech-incubator-reheats-portland-ad-giant-wiedenkennedy/"),
 ("2011","<i>GeekWire</i> &mdash; &ldquo;Fast-growing startup BankSimple flees NYC for Portland: Here&rsquo;s why&rdquo;","https://www.geekwire.com/2011/fastgrowing-startup-banksimple-flees-nyc-portland/"),
 ("2011","<i>GeekWire</i> &mdash; &ldquo;Seattle and Portland should do more to become BFFs&rdquo; (guest column, mine)","https://www.geekwire.com/2011/seattle-portland-bffs/"),
 ("2011","<i>GeekWire</i> &mdash; Quotes of the Week, for publicly begging the internet to resurrect Kozmo","https://www.geekwire.com/2011/and-other-quotes-of-the-week/"),
 ("2012","<i>GeekWire</i> &mdash; &ldquo;Four minutes on the train with&hellip; Rick Turoczy of PIE&rdquo;","https://www.geekwire.com/2012/minutes-train-rick-turoczy/"),
 ("2012","<i>Willamette Week</i> &mdash; &ldquo;Exclusive: New PIE Class Announced&rdquo;","https://www.wweek.com/portland/blog-28909-exclusive-new-pie-class-announced.html"),
 ("2013","Business Wire &mdash; &ldquo;The Silicon Florist Shares Some Secrets of Growing Good Relationships with Bloggers&rdquo;","https://businesswired.wordpress.com/2013/01/24/the-silicon-florist-shares-some-secrets-of-growing-good-relationships-with-bloggers/"),
 ("2013","<i>Willamette Week</i> &mdash; &ldquo;TechfestNW 2013: Rick Turoczy&rdquo;","https://www.wweek.com/portland/article-21061-techfestnw-2013-rick-turoczy.html"),
 ("2014","<i>Portland Monthly</i> &mdash; &ldquo;Reasons to Love Portland: Rick Turoczy,&rdquo; Marty Patail, from the &ldquo;100 Reasons to Love Portland&rdquo; series","https://www.pdxmonthly.com/news-and-city-life/2014/06/rick-turoczy-june-2014"),
 ("2014","<i>Portland Business Journal</i> &mdash; &ldquo;Small Business Awards: Rick Turoczy gets startups off to great starts&rdquo;","https://www.bizjournals.com/portland/print-edition/2014/11/14/small-business-awards-rick-turoczy-gets-startups.html"),
 ("2014","<i>Willamette Week</i> &mdash; PIE Demo Day live stream and report",""),
 ("2015","<i>Portland Monthly</i> &mdash; &ldquo;Hot Tips from Portland&rsquo;s Financial Pros&rdquo;","https://www.pdxmonthly.com/news-and-city-life/2015/01/hot-tips-from-portlands-financial-pros-january-2015"),
 ("2015","<i>Oregon Business</i> &mdash; PIE plans to leave the Wieden+Kennedy building","https://oregonbusiness.com/12056-portland-incubator-experiment-plans-to-leave-wiedenkennedy-building/"),
 ("2015","<i>GeekWire</i> &mdash; PIE closes the accelerator, keeps helping startups","https://www.geekwire.com/2015/portland-incubator-experiment-closes-accelerator-but-still-focused-on-helping-startups/"),
 ("2016","Work With Flux &mdash; on the clearinghouse of 100+ Oregon companies hiring after the Intel layoffs","https://www.workwithflux.com/blog/2016/5/12/intel-layoffs-will-strain-oregon-hiring-capacity-but-help-emerges-for-job-seekers"),
 ("2016","TEDxPortland &mdash; Mara Zepeda and Samuel Hulick, &ldquo;Does technology make you feel more alive?&rdquo;. She calls me a fairy godfather of the Portland startup scene, from the stage, at 5:00.","https://www.youtube.com/watch?v=e4Iul863X-M&amp;t=300s"),
 ("2017","OPB <i>Think Out Loud</i> &mdash; &ldquo;Turkey Trouble | Lead Dust | Makers And Techs,&rdquo; with Marcelino Alvarez, on the split between Oregon&rsquo;s techs and its makers","https://www.opb.org/radio/programs/think-out-loud/article/turkey-lead-tech/"),
 ("2013","OPB <i>Think Out Loud</i> &mdash; &ldquo;Northwest Technology Update.&rdquo; The segment page is gone and nobody archived it.",""),
 ("2019","<i>Willamette Week</i> &mdash; &ldquo;Is Oregon Home to the Next Billion-Dollar Company?&rdquo;","https://www.wweek.com/news/2019/07/03/is-oregon-home-to-the-next-billion-dollar-company/"),
 ("2019","<i>Willamette Week</i> &mdash; &ldquo;Rick Turoczy Says the Myth of the Unflappable Entrepreneur Is All Bullshit&rdquo; (cover profile)","https://www.wweek.com/technology/2019/10/09/rick-turoczy-says-the-myth-of-the-unflappable-entrepreneur-is-all-bullshit/"),
 ("2020","Prosper Portland &mdash; Economic Recovery Task Force, listed across two work groups","https://prosperportland.us/wp-content/uploads/2020/05/Economic-Recovery-Task-Force-Meeting-2.pdf"),
 ("2021","<i>GeekWire</i> &mdash; mpathic and &ldquo;empathy-as-a-service&rdquo; at PIE Demo Day","https://www.geekwire.com/2021/startup-aims-improve-workplace-conversations-empathy-service-software/"),
 ("2021","<i>Willamette Week</i> &mdash; &ldquo;What If You Could Pour Your Own Shampoo From a Tap?&rdquo;","https://www.wweek.com/technology/2021/07/02/what-if-you-could-pump-your-own-shampoo/"),
 ("2008&ndash;09","<i>ReadWriteWeb</i> &mdash; bylined writer on the open web, APIs, and developer hubs outside California","http://web.archive.org/web/20120116011447/http://www.readwriteweb.com:80/archives/readwriteweb_expands_silicon_forest_empire.php"),
]),
("deck", "Books, decks, and masterclasses", [
 ("2026","<i>It Takes a Valley</i>, Anika Horn &mdash; a practitioner&rsquo;s book about the people who build the ecosystems that make entrepreneurship possible. I turn up in it.","https://bookshop.org/p/books/it-takes-a-valley-how-to-build-thriving-entrepreneurial-ecosystems-that-transform-our-communities-anika-horn/24830809?aid=128693&amp;ean=9798995796312&amp;listref=startup-books"),
 ("2020","<i>The Startup Community Way</i>, Brad Feld and Ian Hathaway &mdash; on building complex, founder-led regional ecosystems. I turn up in this one too.","https://bookshop.org/p/books/the-startup-community-way-evolving-an-entrepreneurial-ecosystem-brad-feld/16653612?aid=128693&amp;ean=9781119613602&amp;listref=startup-books"),
 ("2017","<i>Portland Makers: How to Build a Creative Community</i> &mdash; ポートランド・メイカーズ. Mitsuya Mazaki interviewed me in 2016; my words came out in Japanese, and later Korean.","https://book.gakugei-pub.co.jp/gakugei-book/9784761526429/"),
 ("2016&ndash;17","<i>The PIE Cookbook</i> &mdash; everything we learned running PIE, written down and given away open source so any community could run its own accelerator. Kickstarted in 2016; the 0.9 beta landed in 2017.","https://siliconflorist.com/2017/04/04/an-initial-taste-of-the-pie-cookbook/"),
 ("","<i>Brand Signals</i> &mdash; 150 slides on positioning and the things a brand says without saying them","https://www.slideshare.net/slideshow/brand-signals/21148"),
 ("","<i>Inspiring Illogical Decisions</i> &mdash; 50 slides on conviction over incrementalism","https://www.slideshare.net/slideshow/inspiring-illogical-decisions/7124543"),
 ("","<i>A Series of Happy Accidents</i> &mdash; 48 slides on how Portland&rsquo;s scene actually happened","https://www.slideshare.net/slideshow/a-series-of-happy-accidents/55054257"),
 ("","<i>Ideas About Ideas</i> &mdash; 30 slides training executives to mentor founders","https://speakerdeck.com/turoczy/ideas-about-ideas"),
 ("","<i>How to Bake PIE</i> &mdash; 37 slides on accelerator mechanics and cohort design","https://www.slideshare.net/slideshow/how-to-bake-pie-10474833/10474833"),
 ("","<i>PIE: How to Meet</i> &mdash; 18 slides on how a founder meeting should actually go","https://www.slideshare.net/slideshow/pie-how-to-meet/16007393"),
 ("","<i>OEN Social Media 101</i> &mdash; 83 slides of workshop for the Oregon Entrepreneurs Network","https://www.slideshare.net/slideshow/oen-social-media-101-presentation/725914"),
 ("","<i>Tiny Startup Camp: Social Media</i> &mdash; 21 slides, the short version","https://www.slideshare.net/slideshow/tiny-startup-camp-social-media/15146387"),
 ("","<i>2008 Portland Tech Recap</i> &mdash; 64 slides, for PDX Web Innovators","https://www.slideshare.net/slideshow/2008-portland-tech-recap-presentation/816775"),
 ("2025","<i>AI Is Revolutionizing Startup Growth Opportunities Now</i>","https://www.youtube.com/watch?v=dhiYkJBzA5M"),
 ("2025","<i>Securing Funding for Startups Beyond Silicon Valley</i>","https://www.youtube.com/watch?v=QgQlhhBr1eo"),
 ("2022","Founder University &mdash; <i>How to Write Investor Updates</i>, plus the metrics that matter (CAC, LTV, churn)","https://www.youtube.com/watch?v=dgz-Ud4fq6w"),
 ("2020","PIE AMA &mdash; <i>How to find investors in the Portland startup community</i>","https://www.youtube.com/watch?v=tuB_Sc09dmw"),
 ("2020","PIE AMA &mdash; <i>How to join the Portland startup community</i>","https://www.youtube.com/watch?v=x3VeNA8oD60"),
 ("","Masterclasses on YouTube &mdash; starting a startup before building or funding, what founders are actually like, how to mentor, how to Portland startup community",YT),
]),
("kick", "Kickstarter campaigns", [
 ("2016","<i>PIE Cookbook: An Open Source Guide for Startup Accelerators</i> &mdash; crowdfunding the work of writing down everything we learned running PIE, and giving it away","https://www.kickstarter.com/projects/turoczy/pie-cookbook-an-open-source-guide-for-startup-acce"),
 ("2014","<i>Built Oregon</i> &mdash; funding a statewide storytelling project for Oregon&rsquo;s consumer product founders, because nobody was telling those stories either","https://www.kickstarter.com/projects/130336980/built-oregon/"),
]),
("invest", "Things I&rsquo;ve invested in", [
 ("","<i>Airship</i> (neé Urban Airship) &mdash; Portland mobile engagement platform that grew out of the PIE coworking space and went on to raise more than $100M","https://www.airship.com/"),
 ("","<i>Backstage Capital</i> &mdash; Arlan Hamilton&rsquo;s fund backing founders who are underrepresented, underestimated, and usually overlooked","https://backstagecapital.com/"),
 ("","<i>Customer.io</i> &mdash; Portland customer messaging platform, and a charter member of the quiet generation of Portland startups that just execute","https://customer.io/"),
 ("","<i>Graze</i> &mdash; feed-building on Bluesky&rsquo;s open social protocol, so the algorithm is yours instead of somebody else&rsquo;s","https://www.graze.social/"),
 ("","<i>The Sports Bra</i> &mdash; Jenny Nguyen&rsquo;s bar that only shows women&rsquo;s sports, which turned out to be a very good idea","https://thesportsbraofficial.com/"),
 ("","<i>Tender Loving Empire</i> &mdash; Portland record label and craft shops, proving you can build a company out of making things by hand","https://tenderlovingempire.com/"),
]),
("org", "Programming and support", [
 ("2011&ndash;21","<i>TechfestNW</i> &mdash; cofounder and programming curator, with <i>Willamette Week</i>. Multi-track stages, international speakers.","https://web.archive.org/web/20250926091357/https://www.techfestnw.com/"),
 ("2009&ndash;10","<i>30 Hour Day</i> &mdash; a 30-hour livestreamed telethon run out of PIE for Oregon Food Bank, Free Geek, and Toys for Tots. 77,000 viewers, nearly $10,000 raised, and we did it twice.","https://siliconflorist.com/2014/12/19/years-portlands-startup-scene-approaching-long-incredibly-rewarding-day/"),
 ("multiple","<i>PIE Demo Days</i> &mdash; the day each cohort graduates into the ecosystem. Bittersweet every time.","https://www.piepdx.com/"),
 ("2008&ndash;09","<i>Open Source Bridge</i> &mdash; marketing lead for the first one, after OSCON left town","https://web.archive.org/web/20090305100212/http://opensourcebridge.org/"),
 ("2023&ndash;","<i>Pitch Black</i> &mdash; production crew. Stephen Green&rsquo;s pitch competition for Black founders, and the best pitch event in Portland. Every dollar goes to the founders as non-dilutive grants.","https://www.pitchblack.org/"),
 ("2019","<i>Startup Champions Network Spring Summit</i> &mdash; lead organizer and local host, with PIE. Ecosystem builders from around the country spent 2.5 days in Portland, March 19&ndash;21, with panels at the Wacom Experience Center, a public reception at Tilt on East Burnside, and site visits across the city.","https://siliconflorist.com/2019/11/14/revisiting-the-startup-champions-network-portland-visit/"),
 ("2016","<i>Intel Outside</i> &mdash; lead organizer. A free community job fair at the Falcon Building for the ~800 Portlanders laid off by Intel, built from a blog post to nearly 200 supporting companies in four weeks, with no budget.","https://siliconflorist.com/2016/05/24/escalated-quickly-join-free-portland-community-job-fair-june-1-falcon-building/"),
 ("2013","<i>Hack @ Hayward</i> &mdash; Eugene, with Intel, Oregon Film, and TrackTown USA. Two days at Hayward Field imagining the fan experience ahead of the World Junior Championships.",""),
 ("2012","<i>Portland Narrative Hack</i> &mdash; a day with Intel, Wieden+Kennedy, and Oregon Film, hacking the future of interactive storytelling. Sixteen people, no rules. It became Oregon Story Board.","https://vimeo.com/44539955"),
 ("2017&ndash;","<i>Built Festival</i> &mdash; Built Oregon&rsquo;s annual gathering of the state&rsquo;s consumer product founders, makers, and retailers. Started as Built Up Festival in 2017; 700 people across 17 events that first week.","https://www.builtoregon.com/"),
]),
]

def end_year(t):
    t = t.replace('&ndash;','-').strip()
    if not re.search(r'\d', t): return -1
    m = re.match(r'^(\d{4})\s*-\s*(\d{4})$', t)
    if m: return int(m.group(2))
    m = re.match(r'^(\d{4})\s*-\s*(\d{2})$', t)
    if m: return int(m.group(1)[:2]+m.group(2))
    if re.match(r'^\d{4}\s*-\s*$', t): return 9999
    ys = [int(x) for x in re.findall(r'\d{4}', t)]
    return max(ys) if ys else -1

def start_year(t):
    ys = [int(x) for x in re.findall(r'\d{4}', t.replace('&ndash;','-'))]
    return min(ys) if ys else -1

total = sum(len(g[2]) for g in GROUPS)

L = ['  <section class="section" id="index">',
     '    <div class="section-grid">',
     '      <div class="section-head"><h2>Index</h2></div>',
     '      <div class="section-body">',
     '        <p class="lede">Everything I can find a record of &mdash; %d entries and counting. Some of it I remember fondly. Some of it I remember differently than the people who were there.</p>' % total,
     '',
     '        <div class="filters" role="group" aria-label="Filter the index">',
     '          <button type="button" class="chip" data-filter="all" aria-pressed="true">Everything</button>']
for key, lab in [("talk","Talks"),("show pod","Shows"),("press","Press"),("deck","Books &amp; decks"),("kick","Kickstarters"),("invest","Investments"),("org","Organizing")]:
    L.append('          <button type="button" class="chip" data-filter="%s" aria-pressed="false">%s</button>' % (key, lab))
L.append('        </div>')

for key, title, rows in GROUPS:
    ordered = sorted(enumerate(rows), key=lambda t: (-end_year(t[1][0]), -start_year(t[1][0]), t[0]))
    L.append('')
    L.append('        <section class="ix-group" data-group="%s">' % key)
    L.append('          <h3 class="ix-title">%s</h3>' % title)
    L.append('          <ul class="ix">')
    for _, (yr, what, url) in ordered:
        # the entry text IS the link
        body = '<a class="ix-entry" href="%s">%s</a>' % (url, what) if url else what
        L.append('            <li><span class="ix-yr">%s</span><span class="ix-what">%s</span></li>' % (yr or '&nbsp;', body))
    L.append('          </ul>')
    L.append('        </section>')

L += ['',
      '        <p class="ix-note">Missing something? I probably forgot it. <a href="mailto:rick@piepdx.com?subject=You%20forgot%20one">Tell me</a> and I&rsquo;ll add it.</p>',
      '      </div>',
      '    </div>',
      '  </section>']

io.open('/tmp/index_section.html','w',encoding='utf-8').write("\n".join(L)+"\n")
print('entries:', total, '| linked:', sum(1 for g in GROUPS for r in g[2] if r[2]))
