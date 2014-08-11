import ulmo
import db_save

#DB_CONNECTION = 'mysql+pymysql://root:@127.0.0.1/snow'
DB_CONNECTION = 'postgresql+psycopg2://snow:snow@127.0.0.1/snow'
SITE_ID_SKIP = 30000
SITE_ID_MAX = 40000

def save_snow_all():
    #get all the stations
    all_st = ulmo.ncdc.ghcn_daily.get_stations()

    for st_code in all_st:
        site_from_db = db_save.get_site_id(st_code)
        if site_from_db:
            continue
        st_obj = all_st[st_code]
        sno_data = []
        try:
            sno_data = ulmo.ncdc.ghcn_daily.get_data(st_code, elements='SNWD', update=False, as_dataframe=True)
        except:
            print "unable to retrieve snow_data " + st_code
        if (len(sno_data) > 0):        
            ts_list2 = []
            sno = sno_data['SNWD']
            sno2 = sno['value'].dropna()       
            #now get the site id and save site if required
            site_from_db = db_save.get_site_id(st_code)
            if site_from_db == None:
                site_id = db_save.add_site(st_code, st_obj, 1)
            else:
                site_id = site_from_db[0]
            print site_id
            if site_id > SITE_ID_SKIP and site_id <= SITE_ID_MAX:
                #check for NaN!
                for dat, val in sno2.iteritems():
                    iso = dat.start_time.isoformat()
                    dat_s = iso.strip().split('T')
                    dat2 = dat_s[0]
                    val2 = {'time': dat2, 'site_id': site_id, 'qualifier': 1, 'val': round(val/10)}
                    if val2['val'] > 0:
                        ts_list2.append(val2)

                if len(ts_list2) > 0:
                    try:
                        db_save.add_values(ts_list2)
                        print st_code + ' ' + st_obj['name'] + ' saved: ' + str(len(ts_list2))	
                    except:
                        print "cannot save values to db"				

				
if __name__ == "__main__":
    db_save.DB_CONNECTION = DB_CONNECTION
    save_snow_all()	