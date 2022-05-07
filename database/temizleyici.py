import logging
import re
logger = logging.getLogger(__name__)

def temizle(text):
    try:
        # deemoji
        regrex_pattern = re.compile(pattern = "["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                            "]+", flags = re.UNICODE)
        abo = regrex_pattern.sub(r'',text).lower()
        abo = abo.replace('  ', ' ')
        abo = abo.replace('adlı dosyanın kopyası', '')
        abo = abo.replace('soru bankası çözümlü', 'çsb')
        abo = abo.replace('çözümlü soru bankası', 'çsb')
        abo = abo.replace('özetli soru bankası', 'ösb')
        abo = abo.replace('konu anlatımlı', 'ka')
        abo = abo.replace('konu özetli', 'kö')
        abo = abo.replace('sorubankası', 'sb')
        abo = abo.replace('soru bankası', 'sb')

        abo = abo.replace('final dergisi dershaneleri', 'final yay')
        abo = abo.replace('sınav dergisi dershaneleri', 'sınav yay')
        abo = abo.replace('dershaneleri', 'drshne')

        abo = abo.replace('@pdfmekani', '')
        abo = abo.replace('@egitimkitaplari', '')
        abo = abo.replace('@egitimgrup', '')
        abo = abo.replace('benim hocam', 'bh')
        abo = abo.replace('@osymdokuman', '')
        abo = abo.replace('@yks 2020pdf', '')
        abo = abo.replace('@gncpdfkanali', '')
        abo = abo.replace('@ogrencixevi', '')
        abo = abo.replace('@ogrencievi', '')
        abo = abo.replace('@turkleech', '')
        abo = abo.replace('@ydtteam', '')
        abo = abo.replace('@kitapdolabi', '')
        abo = abo.replace('@kitapbol paylaşımıdır', '')
        abo = abo.replace('@kitapbol', '')
        abo = abo.replace('@dkitap', '')
        abo = abo.replace('@yksor2021', '')
        abo = abo.replace('@tgarsiv', '')
        abo = abo.replace('@sanalkitap', '')
        abo = abo.replace('@cinciva', '')
        abo = abo.replace('@pdf kitablar', '')
        abo = abo.replace('@kitupchi', '')

        abo = abo.replace('pdfdrive com', '')
        abo = abo.replace('pdfdrive', '')
        abo = abo.replace('compressed', 'kçk')
        abo = abo.replace('pdfkitabevim com', '')
        abo = abo.replace('@akiraninkitapdunyasi', '')
        abo = abo.replace('@akirasbookworld', '')
        abo = abo.replace('pdf indir', 'pdf')
        abo = abo.replace('pdfdrivecom', '')
        abo = abo.replace('ekitappdfoku com', '')
        abo = abo.replace('www booktandunya com', '')
        abo = abo.replace('booktandunya com', '')
        abo = abo.replace('bedavapdf com', '')
        abo = abo.replace('pdfarsiv com', '')
        abo = abo.replace('www arsivciniz com', '')
        abo = abo.replace('arsivciniz com', '')
        abo = abo.replace('şifre www kitapfan com', '')
        abo = abo.replace('www kitapfan com', '')
        abo = abo.replace('kitapfan com', '')
        abo = abo.replace('şifre www twilightturk com', '')
        abo = abo.replace('www twilightturk com', '')
        abo = abo.replace('twilightturk com', '')
        abo = abo.replace('şifre webcanavari net', '')
        abo = abo.replace('webcanavari net', '')

        abo = abo.replace('bahar dönemi', 'bahar')
        abo = abo.replace('güz dönemi', 'güz')

        abo = abo.replace('yayınları', 'yay')
        abo = abo.replace('yayınevi', 'yay')
        abo = abo.replace('yayıncılık', 'yay')
        abo = abo.replace('yayınlar', 'yay')
        abo = abo.replace('dershaneleri', 'drsahi')
        abo = abo.replace('yayın nları', 'yay')
        abo = abo.replace('yayınlaır', 'yay')
        abo = abo.replace('kitabevi', 'ktbvi')


        abo = abo.replace('pdf pdf', 'pdf', 60)
        abo = abo.replace('epub epub', 'epub', 60)
        abo = abo.replace('pdf indir', '')

        abo = abo.replace('paragraf', 'pgrf')
        abo = abo.replace('matematik', 'mtik')
        abo = abo.replace('geometri', 'gtri')
        abo = abo.replace('türkçe', 'trkç')
        abo = abo.replace('biyoloji', 'bylj')
        abo = abo.replace('edebiyat', 'ebyt')
        abo = abo.replace('coğrafya', 'cfya')

        abo = abo.replace('eşit ağırlık', 'ea')
        abo = abo.replace('sayısal', 'say')
        abo = abo.replace('sözel', 'söz')

        abo = abo.replace('trigonometri', 'trgnmtri')
        
        abo = abo.replace('=', '')
        abo = abo.replace("'", '')
        abo = abo.replace('#', '')

        # boşlukla
        abo = re.sub(r'[\.\+\-\_\(\)\s\–\,\^\'\™\!\0\t]+',' ', abo, count=60)
        abo = abo.replace('  ', ' ', 60).strip().strip(' ')

        # ikiye böl
        # a = abo.split(' ')
        # s1=s2=""
        # for word in a:
        #     if len(s1) >= 30: s2+=word + " "
        #     else: s1+=word + " "
        # s1=s1.strip(' ').strip()
        # s2=s2.strip(' ').strip()
        # if len(s2) != 0: s1 = s1 + "\n" + s2
        # s1=s1.replace(' ', '.')
        # print(s1)
        # abo = s1

        return abo.replace(' ', '.')
    except Exception as e:
        logger.error(e)
        return text

def cleanhtml(raw_html):
    try:
        CLEANR = re.compile('<.*?>')
        a = re.sub(CLEANR, '', raw_html)
        a = a.replace('\n', ' ', 60)
        return a
    except Exception as e:
        logger.error(e)
        return raw_html
