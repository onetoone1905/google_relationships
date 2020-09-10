
keyword="covid"
#### Extracting url from google results
def get_url(keyword, lang='french'):
    if lang!='french':
        url='https://www.google.com/search?hl=en&q='+keyword.replace(' ','+')
    else :
        url = 'https://www.google.com/search?&q='+keyword.replace(' ','+')

    page = requests.get(url)
    soup = BeautifulSoup(page.content)

    list_url= []
    for bibi in soup.find_all('a'):
        list_url.append(bibi.get('href'))

    final_url=[]
    for url in list_url:
        m = re.search('url\?q=(.+?)&sa', url)     ####/!\ 'sa'
        #if url.startswith('/url'):
        if m:
            #final_url.append(url.replace('/url?q=', ''))
            final_url.append(m.group(1))
    #### Only first ten sites (the more depth the less linked to the keyword)
    # Also making sure all url are unique
    final_url=list(set(final_url[:10]))
    return final_url
####Extracting soup from each url
def get_soups(final_url):
    timer=len(final_url)

    checked_url=[]
    final_soups=[]
    for i, url in enumerate(final_url):
        #print(i,'/',timer)
        print("Progress {0}".format(i+1),"/",timer, end="\r")
        try :
            page = requests.get(url)
            soup = BeautifulSoup(page.content)
            final_soups.append(soup)
            checked_url.append(url)
        except:
            print("Site rejected agent, trying next url")
    print("")    
    return final_soups, checked_url
#### Cleaning each soup to get the text 
def cleanhtml(raw_html):
    cleanr1 = re.compile('href=\"*?\"')
    raw_html = re.sub(cleanr1, '', raw_html)
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, ' ', raw_html)
    
    #cleantext = re.sub(r"http\S+", "", cleantext)
    return cleantext
def clean_soups(final_soups):
    final_soup_clean=[]
    for soup in final_soups:
        clean_soup=[]
        for div in soup.find_all("div", {'class':'marg-btm-xs'}):
            div.decompose()
        for div in soup.find_all("li") : #find_all("div", {'class':'marg-btm-xs'}):
            div.decompose()
        soup=soup.find_all('p')
        for paraph in soup : 
            clean_soup.append(cleanhtml(str(paraph)))
        final_soup_clean.append(' '.join(str(elem) for elem in clean_soup))
    return final_soup_clean
#### Cleaning each text we got
def clean_text(input_str): 
    input_str=re.sub('-',' ',input_str)
    input_str=re.sub('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', ' ', input_str)
    ## Remove number
    result = re.sub(r'\d+', ' ', input_str)
    ## Remove punctuation
    result=re.sub('\'',' ', result)
    result=result.translate(result.maketrans('', '', string.punctuation))
    ## Remove whitespace
    result = result.strip()
    ## Special caract
    result=re.sub('\W+',' ', result)
    
    result=''.join(c for c in unicodedata.normalize('NFD', result) if unicodedata.category(c) != 'Mn')
    return result.lower()
def clean_texts(final_soups_clean):
    pretty_clean=[]
    for he in final_soups_clean : ### A corriger [:-4]
        pretty_clean.append(clean_text(he))
    return pretty_clean

#### Getting rid of stopwords and tokenizing
def tokenize(pretty_clean, lang):
    token_article=[]
    stop_words = set(stopwords.words(lang)) 
    for text in pretty_clean:
        token_article_temp = word_tokenize(text)
        filtered_sentence = [w for w in token_article_temp if not w in stop_words] 
        token_article.append(filtered_sentence)
    return token_article

#### All together to have a corpus very quick
def corpus_this(keyword, lang):
    final_url=get_url(keyword, lang)
    final_soups, checked_url=get_soups(final_url)
    pretty_clean_soups=clean_texts(clean_soups(final_soups))
    corpus=' '.join(str(elem) for elem in pretty_clean_soups)
    token_articles=tokenize(pretty_clean_soups, lang)
    titles=[]
    for url in checked_url :
        s = url
        result = re.search('.\.(.*)\..*/', s)
        try : 
            titles.append(result.group(1))
        except : 
            titles.append(url)
    return corpus, token_articles, pretty_clean_soups, titles
