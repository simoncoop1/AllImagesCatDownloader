import urllib.parse
import urllib.request
import json
import re
import pathlib
import os
import pdb
import time
import sys
from SPARQLWrapper import SPARQLWrapper, JSON

#user set variables -start
#set the variables in this this block before running
#eg. /home/yourname/yourprojectname/
basefldr ='' 
# the 'cookie'value of http request for a logged in session at /
# https://commons-query.wikimedia.org/sparql
# e.g will look like "GeoIP=GB:location:32.31:-3.30:v3; wcqsSession=eXAiOiJKV1QiLCJhdfdasfbGciOiJIUzI1NiJ9.eyJfdaffdfoiU2ltb25jMTExIn0.DMNfdsataOX3M_Gasdf5f_QhqEE-rb9DA; wcqsOauth=1c9ffsa96a7a84a76e3916117.fdsa3f3d84711636c65122de950"
# NOTE - script will not function without this
cookie = ""
# the name of the common category you want to download all the /
# images for. e.g 'Bucephala clangula'
cat = 'Bucephala clangula'
# an optional wikidata item, if a value is set, the wikidata items's /
# site-link for commons will be used as a starting category. e.g 'Q579718'
WDitem=""
#WDitem="Q190342"
#limit the number of results
limit = 20
#set a timeout between downloads to avoid
intervalTimeout=0
#user set variables - end-

user_agent = 'AllImagesCatDownloader/0.1 bot (https://github.com/simoncoop1/AllImagesCatDownloader, [[d:User_talk:Simonc8]]) SPARQLWrapper'

endpoint_url = "https://commons-query.wikimedia.org/sparql"

query = """#defaultView:Table
SELECT distinct ?file ?title  ?image  ?d ?e ?elabel ?contentUrl ?g
WITH
{
  SELECT ?file ?title ?size
  WHERE
  {
    SERVICE wikibase:mwapi
    {
      bd:serviceParam wikibase:api "Generator" .
      bd:serviceParam wikibase:endpoint "commons.wikimedia.org" .
      bd:serviceParam mwapi:gcmtitle "Category:River Ravensbourne" .
      bd:serviceParam mwapi:generator "categorymembers" .
      bd:serviceParam mwapi:gcmtype "file" .
      bd:serviceParam mwapi:gcmlimit "max" .
      ?title wikibase:apiOutput mwapi:title .
      ?pageid wikibase:apiOutput "@pageid" .
      bd:serviceParam mwapi:prop "imageinfo".
      ?size wikibase:apiOutput "imageinfo/ii/@size".
    }
    BIND (URI(CONCAT('https://commons.wikimedia.org/entity/M', ?pageid)) AS ?file)
  }
} AS %get_files
WHERE
{
  
  INCLUDE %get_files
         
     #?file      p:P170 ?author .
  #SERVICE <https://query.wikidata.org/sparql> {
  # ?author ?athing ?authorLabel .
    
 
  #  FILTER (lang(?capturedWithLabel) = "en")
  #  ?author ?z ?authorString
    
   
  #}
  #OPTIONAL {?file wdt:P170 ?author}.

  #OPTIONAL {?file wdt:P1259 ?coords} .  # coords of POV      
  #OPTIONAL {?file wdt:P9149 ?coords} .  # fallback: coords of depicted place
  #OPTIONAL { ?p170 wdt:P7763 ?copyright_status. 
  #               ?copyright_status rdfs:label ?copyright_statusLabel
  #               filter (lang(?copyright_statusLabel) = "en")
  #             }
  ?file p:P275 ?value.
  optional {?value 	ps:P275 ?e.}.
  ?file p:P170/pq:P2093 ?g.
  #FILTER(bound(?coords)) .
  ?file schema:url ?image.
  ?file schema:contentUrl ?contentUrl.
    service <https://query.wikidata.org/sparql> {
    OPTIONAL {?e rdfs:label ?elabel  FILTER (lang(?elabel) = 'en').  } 
    }
  #?e ?f ?p.
   #?file p:P275/ps:P275 ?da.
 
  
  SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
      
}
ORDER BY DESC(?file)
limit 100"""

def get_results(endpoint_url, query, cookie):
    sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
    #sparql.addCustomHttpHeader('Authorization','Bearer '+accessToken)
    sparql.addCustomHttpHeader('Cookie', cookie)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()

#results = get_results(endpoint_url, query, cookie)
#for result in results["results"]["bindings"]:
#    print(result)

def getSubCats(startingCat, cookie):
    petscanurl="""https://petscan.wmcloud.org/?interface_language=en&maxlinks=&ores_prediction=any&output_compatability=catscan&max_sitelink_count=&edits[bots]=both&categories=Bucephala+clangula&search_max_results=500&cb_labels_any_l=1&manual_list_wiki=&negcats=&show_redirects=both&wikidata_label_language=&min_redlink_count=1&min_sitelink_count=&sitelinks_yes=&edits[flagged]=both&links_to_any=&active_tab=tab_output&language=commons&project=wikimedia&sitelinks_any=&labels_yes=&show_disambiguation_pages=both&cb_labels_no_l=1&show_soft_redirects=both&langs_labels_no=&ns[14]=1&outlinks_yes=&manual_list=&depth=6&since_rev0=&search_wiki=&common_wiki_other=&subpage_filter=either&smaller=&cb_labels_yes_l=1&minlinks=&labels_any=&sortorder=ascending&referrer_url=&common_wiki=auto&doit=&format=json"""
    petscanurl=re.sub(r'categories=Bucephala\+clangula', 'categories='+urllib.parse.quote_plus(startingCat), petscanurl)
    headers={'User-Agent': user_agent,'Cookie':cookie}
    req = urllib.request.Request(petscanurl, None, headers)
    with urllib.request.urlopen(req) as response:
        jsonR = json.loads(response.read())
    subcats = jsonR['*'][0]['a']['*']
    return subcats

#a category is obtained from petscan, and used for sparql query
def SparqlCommonsCat(endpoint_url,query, cookie, cat):
    return get_results(endpoint_url, re.sub(r'Category:River Ravensbourne','Category:'+cat, query), cookie)

def go():
    #get subcategories
    pscats =getSubCats(cat, cookie)
    #add the initial category
    pscats.append(dict(title=cat.replace(' ', '_') ))
    somer=[]
    for apcat in pscats:
        r = SparqlCommonsCat(endpoint_url,query, cookie, apcat['title'].replace('_',' '))
        somer+=r['results']['bindings']
    return somer

#variable is pathlib.path object for the species
def download(alist,path, startCat):
    
    for s in alist[:limit]:
        contentURL=s['contentUrl']['value']
        nm=s['contentUrl']['value'].split('/')[-1]
        p = pathlib.Path(os.path.join(path,startCat))
        if not p.exists():
            p.mkdir()
        with urllib.request.urlopen(contentURL) as response:
             with open(os.path.join(str(p),nm), 'bw+') as f:
                f.write(response.read())
        #the meta data
        nmm='.'.join(nm.split('.')[:-1])+'.json'
        with open(os.path.join(str(p),nmm), 'w+') as f:
             f.write(json.dumps([dict(license=s['elabel']['value'], author=s['g']['value'],title=s['title']['value'], contentUrl=s['contentUrl']['value'], commonsUrl=s['file']['value'])]))

# parameter is a Wikidata item e.g 'Q29865' and returns the name of a /
# commons category if it exits
def categoryFromWikidataItem(WDitem):
    query = """#for a given Wikidata item get commons site link
SELECT ?item ?itemLabel ?article ?articleLabel
WHERE
{
  bind(wd:Q29865 as ?item)
  ?article schema:about ?item .
  ?article schema:isPartOf <https://commons.wikimedia.org/>.
  SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". } # Helps get the label in your language, if not, then en language
}"""
    query= re.sub('Q29865', WDitem, query)
    endpoint_url = "https://query.wikidata.org/sparql"
    sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    r= sparql.query().convert()
    if r['results']['bindings'] == []:
        return None
    else:
        sl =r['results']['bindings'][0]['articleLabel']['value'].split('/')[-1]
        return  (':'.join(sl.split(':')[1:]) if sl.lower().startswith('category:') else sl).replace('_', ' ')

#run script
cat=categoryFromWikidataItem(WDitem)
somer=go()
download(somer, basefldr, cat)
