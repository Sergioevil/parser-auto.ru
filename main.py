import requests
import re
import gspread
import os

headers = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-GB,en;q=0.9,en-US;q=0.8,ru;q=0.7",
    "Connection": "keep-alive",
    "content-type": "application/json",
    "Cookie": 'suid=e43c5aa249a18f69c3a66ac8ffc62e0e.f04d8588bdea97f134f9f7ba4552827c; autoru_sid=a%3Ag635e23922b96uls6m6n5h4idh1prsv4.f29cbde9aae679ad201ef86126b5a67b%7C1667113874048.604800.Be3P84M52i-GLBWGaaNSzA.pVdRyjhsn8Pvf8HkRU5NzeVWFW7WTeZIuOOK16jsBfY; autoruuid=g635e23922b96uls6m6n5h4idh1prsv4.f29cbde9aae679ad201ef86126b5a67b; autoru_gdpr=1; gdpr=0; _ym_isad=2; _ym_uid=1654634294220843093; _ym_visorc=b; spravka=dD0xNjY3MTEzODkwO2k9MTg4LjI0Ny4yMTguMTM2O0Q9MjRBNjU1QzM3QkZFNDY3N0U1OTI4MDRGN0VCOTQ1OEY4OTI2MzRCNjI2QkZBNTMyNEU1QjQ2MDVFNjJGQzgwRUY4QkI1MDEyO3U9MTY2NzExMzg5MDUxOTcwNjQ3MTtoPWZjMGFiZTMzOWQzNmFjMzFlOGQ4ODYyZTg3OWY3ODUw; _csrf_token=2003fabfb91c1dcc9c9d6466ac84b0654c339f9ea471abeb; from=direct; yuidlt=1; yandexuid=5725083331650441106; counter_ga_all7=2; pdd_exam_popup_hide=true; _yasc=G9mKzDNR+TyYMxxEN05UJxmw7azWbnbiIhAOUMwH9pnqZAv8scyL/Kt2fMo2qA==; Session_id=3:1667113942.5.0.1654675922393:Kn-B1Q:16.1.2:1|1130000055548335.0.2|61:10008484.370302.qW8pOP6cSClMVch8DDJbjuu9ZkI; yandex_login=spurik@fromtech.ru; ys=udn.cDpzcHVyaWtAZnJvbXRlY2gucnU%3D#c_chck.1781532142; i=lnNuqfcFNVl1I91dF4pedjHcQtJCvNkzUIX86xKA+31eT0FN7f07h2RjWWFxN6yoOnY8eowWZ/+zpR7fh9p3Mu+GLz8=; mda2_beacon=1667113942434; sso_status=sso.passport.yandex.ru:synchronized; from_lifetime=1667114257630; _ym_d=1667114257; layout-config={"win_width":738.4000244140625,"win_height":632.7999877929688}',
    "Host": "auto.ru",
    "Origin": "https://auto.ru",
    "sec-ch-ua": '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "Windows",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "same-origin",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36",
    "x-client-app-version": "187.0.10246046",
    "x-client-date": "1667114314839",
    "x-csrf-token": "2003fabfb91c1dcc9c9d6466ac84b0654c339f9ea471abeb"
}

def get_data(model_page):
    models, page = model_page

    # change your settings 
    payload = {
        "year_from": 2018, 
        "year_to": 2019, 
        "catalog_filter": models, 
        "section": "all",
        "page": page,
        "category": "cars",
        "output_type": "list"
        }

    r = requests.post("https://auto.ru/-/ajax/desktop/listing/", json=payload, headers=headers)
    
    try:
        data = r.json()
    except:
        data = []
    r.close()
    return data


def main(models, sh):
    data_to_out = []
    pages = get_data((models,1)).get('pagination').get('total_page_count')
    for p in range(1, int(pages)+1):
        data = get_data((models, p))
        if data:
            all_offers = data.get('offers')
            for offer in all_offers:
                model = ''
                name = ''
                condition=''
                year=''
                probeg=''
                volume_engine=''
                price=''
                name = offer.get('vehicle_info').get('tech_param').get('human_name')
                model = offer.get('vehicle_info').get('model_info').get('name')
                if 'no_accidents' in offer.get('tags'):
                    condition = 'Не битая'
                else:
                    condition = 'Неизвестно'
                year = offer.get('documents').get('year')
                probeg = offer.get('state').get('mileage')
                get_volume = re.search(r'(\d\.\d)', offer.get('vehicle_info').get('tech_param').get('human_name'))
                if get_volume:
                    volume_engine = get_volume.group(1)
                else:
                    volume_engine = ''
                price = offer.get('price_info').get('USD')
                engine = offer.get('vehicle_info').get('tech_param').get('engine_type')
                data_to_out.append((models[0].get('mark'), model ,name, engine, condition, year, probeg, volume_engine, price))
    
    try:
        # Creating list if not exists
        sh.add_worksheet(models[0].get('mark'), 1000, 20)
    except:
        pass
    wks1 = sh.worksheet(models[0].get('mark'))
    wks1.update(f"A1:I1", [['марка', 'модель', 'название', 'двигатель', 'состояние', 'год', 'пробег', 'объем двигателя', 'цена (USD)']])
    wks1.update(f"A2:I{len(data_to_out)+1}", data_to_out)


if __name__ == "__main__":
    models_to_parse_list = [
        # [{"mark": "CHEVROLET", "model": "AVEO"},
        # {"mark": "CHEVROLET", "model": "CAPTIVA"},
        # {"mark": "CHEVROLET", "model": "CRUZE"},
        # {"mark": "CHEVROLET", "model": "LACETTI"},
        # {"mark": "CHEVROLET", "model": "LANOS"}], 
        
        # [{"mark": "BMW", "model": "3ER"},
        # {"mark": "BMW", "model": "5ER"},
        # {"mark": "BMW", "model": "X3"},
        # {"mark": "BMW", "model": "X4"},
        # {"mark": "BMW", "model": "X5"},
        # {"mark": "BMW", "model": "X6"},
        # {"mark": "BMW", "model": "X7"}],

        # [{"mark": "FORD", "model": "EXPLORER"},
        # {"mark": "FORD", "model": "FOCUS"},
        # {"mark": "FORD", "model": "KUGA"}],

        # [{"mark": "HONDA", "model": "ACCORD"},
        # {"mark": "HONDA", "model": "CIVIC"},
        # {"mark": "HONDA", "model": "CR_V"}],

        # [{"mark": "HYUNDAI", "model": "CRETA"},
        # {"mark": "HYUNDAI", "model": "ELANTRA"},
        # {"mark": "HYUNDAI", "model": "PALISADE"},
        # {"mark": "HYUNDAI", "model": "SANTA_FE"},
        # {"mark": "HYUNDAI", "model": "SOLARIS"},
        # {"mark": "HYUNDAI", "model": "SONATA"},
        # {"mark": "HYUNDAI", "model": "TUCSON"}],

        # [{"mark": "JEEP", "model": "COMPASS"},
        # {"mark": "JEEP", "model": "GLADIATOR"},
        # {"mark": "JEEP", "model": "GRAND_CHEROKEE"},
        # {"mark": "JEEP", "model": "WRANGLER"}],

        # [{"mark": "INFINITI", "model": "QX50"},
        # {"mark": "INFINITI", "model": "QX55"},
        # {"mark": "INFINITI", "model": "QX60"},
        # {"mark": "INFINITI", "model": "QX80"}], 

        # [{"mark": "KIA", "model": "CEED"},
        # {"mark": "KIA", "model": "CERATO"},
        # {"mark": "KIA", "model": "K5"},
        # {"mark": "KIA", "model": "RIO"},
        # {"mark": "KIA", "model": "SORENTO"},
        # {"mark": "KIA", "model": "SOUL"},
        # {"mark": "KIA", "model": "SPORTAGE"}],

        # [{"mark": "LAND_ROVER", "model": "DEFENDER"},
        # {"mark": "LAND_ROVER", "model": "DISCOVERY"},
        # {"mark": "LAND_ROVER", "model": "DISCOVERY_SPORT"},
        # {"mark": "LAND_ROVER", "model": "EVOQUE"},
        # {"mark": "LAND_ROVER", "model": "RANGE_ROVER"},
        # {"mark": "LAND_ROVER", "model": "RANGE_ROVER_SPORT"},
        # {"mark": "LAND_ROVER", "model": "RANGE_ROVER_VELAR"}],

        # [{"mark": "LEXUS", "model": "ES"},
        # {"mark": "LEXUS", "model": "GX"},
        # {"mark": "LEXUS", "model": "IS"},
        # {"mark": "LEXUS", "model": "LX"},
        # {"mark": "LEXUS", "model": "NX"},
        # {"mark": "LEXUS", "model": "RX"},
        # {"mark": "LEXUS", "model": "UX"}],

        # [{"mark": "MINI", "model": "CLUBMAN"},
        # {"mark": "MINI", "model": "COUNTRYMAN"},
        # {"mark": "MINI", "model": "HATCH"}],

        # [{"mark": "MAZDA", "model": "3"},
        # {"mark": "MAZDA", "model": "6"},
        # {"mark": "MAZDA", "model": "CX_30"},
        # {"mark": "MAZDA", "model": "CX_4"},
        # {"mark": "MAZDA", "model": "CX_5"},
        # {"mark": "MAZDA", "model": "CX_9"},
        # {"mark": "MAZDA", "model": "DEMIO"}],

        # [{"mark": "MERCEDES", "model": "C_KLASSE"},
        # {"mark": "MERCEDES", "model": "E_KLASSE"},
        # {"mark": "MERCEDES", "model": "GLC_KLASSE"},
        # {"mark": "MERCEDES", "model": "GLE_KLASSE"},
        # {"mark": "MERCEDES", "model": "GLS_KLASSE"},
        # {"mark": "MERCEDES", "model": "G_KLASSE"},
        # {"mark": "MERCEDES", "model": "S_KLASSE"}],

        # [{"mark": "MITSUBISHI", "model": "ASX"},
        # {"mark": "MITSUBISHI", "model": "ECLIPSE_CROSS"},
        # {"mark": "MITSUBISHI", "model": "L200"},
        # {"mark": "MITSUBISHI", "model": "MONTERO_SPORT"},
        # {"mark": "MITSUBISHI", "model": "OUTLANDER"},
        # {"mark": "MITSUBISHI", "model": "PAJERO"},
        # {"mark": "MITSUBISHI", "model": "PAJERO_SPORT"}],

        # [{"mark": "NISSAN", "model": "X_TRAIL"},
        # {"mark": "NISSAN", "model": "QASHQAI"},
        # {"mark": "NISSAN", "model": "TERRANO"},
        # {"mark": "NISSAN", "model": "ALMERA"},
        # {"mark": "NISSAN", "model": "NOTE"},
        # {"mark": "NISSAN", "model": "PATHFINDER"},
        # {"mark": "NISSAN", "model": "MURANO"}],

        # [{"mark": "PORSCHE", "model": "911"},
        # {"mark": "PORSCHE", "model": "BOXSTER"},
        # {"mark": "PORSCHE", "model": "CAYENNE"},
        # {"mark": "PORSCHE", "model": "CAYMAN"},
        # {"mark": "PORSCHE", "model": "MACAN"},
        # {"mark": "PORSCHE", "model": "PANAMERA"},
        # {"mark": "PORSCHE", "model": "TAYCAN"}],

        # [{"mark": "RENAULT", "model": "ARKANA"},
        # {"mark": "RENAULT", "model": "DOKKER"},
        # {"mark": "RENAULT", "model": "DUSTER"},
        # {"mark": "RENAULT", "model": "KAPTUR"},
        # {"mark": "RENAULT", "model": "LOGAN"},
        # {"mark": "RENAULT", "model": "MEGANE"},
        # {"mark": "RENAULT", "model": "SANDERO"}],

        # [{"mark": "SKODA", "model": "FABIA"},
        # {"mark": "SKODA", "model": "KAROQ"},
        # {"mark": "SKODA", "model": "KODIAQ"},
        # {"mark": "SKODA", "model": "OCTAVIA"},
        # {"mark": "SKODA", "model": "RAPID"},
        # {"mark": "SKODA", "model": "SUPERB"},
        # {"mark": "SKODA", "model": "YETI"}], 

        # [{"mark": "SUZUKI", "model": "JIMNY"},
        # {"mark": "SUZUKI", "model": "SWIFT"},
        # {"mark": "SUZUKI", "model": "SX4"},
        # {"mark": "SUZUKI", "model": "VITARA"}],

        # [{"mark": "SUBARU", "model": "ASCENT"},
        # {"mark": "SUBARU", "model": "FORESTER"},
        # {"mark": "SUBARU", "model": "LEGACY"},
        # {"mark": "SUBARU", "model": "OUTBACK"},
        # {"mark": "SUBARU", "model": "XV"}],

        # [{"mark": "TOYOTA", "model": "CAMRY"},
        # {"mark": "TOYOTA", "model": "COROLLA"},
        # {"mark": "TOYOTA", "model": "HILUX"},
        # {"mark": "TOYOTA", "model": "LAND_CRUISER"},
        # {"mark": "TOYOTA", "model": "LAND_CRUISER_PRADO"},
        # {"mark": "TOYOTA", "model": "RAV_4"}],

        # [{"mark": "TESLA", "model": "MODEL_3"},
        # {"mark": "TESLA", "model": "MODEL_S"},
        # {"mark": "TESLA", "model": "MODEL_X"},
        # {"mark": "TESLA", "model": "MODEL_Y"}],

        # [{"mark": "VOLKSWAGEN", "model": "MULTIVAN"},
        # {"mark": "VOLKSWAGEN", "model": "PASSAT"},
        # {"mark": "VOLKSWAGEN", "model": "POLO"},
        # {"mark": "VOLKSWAGEN", "model": "TAOS"},
        # {"mark": "VOLKSWAGEN", "model": "TERAMONT"},
        # {"mark": "VOLKSWAGEN", "model": "TIGUAN"},
        # {"mark": "VOLKSWAGEN", "model": "TOUAREG"}],

        # [{"mark": "VOLVO", "model": "S60"},
        # {"mark": "VOLVO", "model": "S90"},
        # {"mark": "VOLVO", "model": "V60_CROSS_COUNTRY"},
        # {"mark": "VOLVO", "model": "V90_CROSS_COUNTRY"},
        # {"mark": "VOLVO", "model": "XC40"},
        # {"mark": "VOLVO", "model": "XC60"},
        # {"mark": "VOLVO", "model": "XC90"}]
    ]
    gc = gspread.service_account(filename=os.path.abspath('main.py')[:-7]+'service_account.json')
    
    # You must create table before parsing
    # Your table name
    sh = gc.open('auto_ru')
    for i in models_to_parse_list:
        main(i, sh)
