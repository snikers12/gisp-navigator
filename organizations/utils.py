import csv
import json
import os
import xml.etree.ElementTree as ET
from xml.dom import minidom
import pylightxl as xl
from organizations.models import Organization, Subsidies, SupportMeasures, Okved, Branch, Tass, \
    Region, SupportMeasuresTypes, OrganizationSize


# from organizations.utils import get_winners_from_json

def get_winners(data):
    for el in data:
        if (el['grbs']['inn'] == '7705596339'):
            region, created = Region.objects.get_or_create(
                region_code=el['receiver'][0]['localAddress']['regionCodeFixed'],
                region_name=el['receiver'][0]['localAddress']['regionName']
            )
            organization, created = Organization.objects.get_or_create(
                inn=el['receiver'][0]['inn'])
            organization.ogrn = el['receiver'][0]['ogrn']
            organization.region = region
            organization.found_date = el['grbs']['dateAccount']['$date'].split('T')[0]
            organization.save()
            if el['plans']:
                for plan in el['plans']:
                    support_measure, created = SupportMeasures.objects.get_or_create(
                        kbk=plan['kbk'])
                    support_measure.name = plan['purpose']
                    support_measure.is_federal = (
                        True if el['grbs']['budgtypename'] == 'Федеральный бюджет' else False)
                    support_measure.save()
                    Subsidies.objects.create(
                        organization=organization,
                        date_received=el['info']['dateAgreem']['$date'].split('T')[0],
                        sum=plan['sumTotal']
                    )
            elif el['plansNormalized']:
                for plan in el['plansNormalized']:
                    support_measure, created = SupportMeasures.objects.get_or_create(
                        kbk=plan['kbkCode'])
                    support_measure.name = plan['purpose']
                    support_measure.is_federal = (
                        True if el['grbs']['budgtypename'] == 'Федеральный бюджет' else False)
                    support_measure.save()
                    Subsidies.objects.create(
                        organization=organization,
                        date_received=el['info']['dateAgreem']['$date'].split('T')[0],
                        sum=plan['sumTotal'], support_measure=support_measure
                    )


def get_winners_from_json():
    for i in range(1, 21):
        with open(os.path.join(os.path.dirname(__file__), f'data/subs/{i}.json')) as jf:
            data = json.loads("[" +
                              jf.read().replace("}\n{", "},\n{") +
                              "]")
            get_winners(data)
        print(i)


# from organizations.utils import get_okveds2
def get_okveds2():
    path = os.path.join(os.path.dirname(__file__), 'data/excels/gisp.xlsx')
    db = xl.readxl(path)
    ws = db.ws('сводная информация')
    data = list(ws.rows)
    for row in data[2:]:
        if not row[3]:
            continue
        inn = row[18]
        organization = Organization.objects.filter(inn=inn).first()
        okveds = row[3].split('/')
        try:
            okveds_data = []
            for el in okveds:
                name = el.split('[')
                code = name[1].split(']')[0]
                name = name[0]
                okveds_data.append([name, code])
            attach = []
            for el in okveds_data:
                okved, created = Okved.objects.get_or_create(code=el[1], name=el[0])
                attach.append(okved)
            if organization and attach:
                organization.okveds.add(*attach)
        except:
            continue


# from organizations.utils import get_branches
def get_branches():
    path = os.path.join(os.path.dirname(__file__), 'data/excels/gisp.xlsx')
    db = xl.readxl(path)
    ws = db.ws('сводная информация')
    data = list(ws.rows)
    for row in data[2:]:
        if not row[16]:
            continue
        inn = row[18]
        organization = Organization.objects.filter(inn=inn).first()
        branches = row[16].split('/')
        try:
            branches_data = []
            for el in branches:
                name = el.split('[')
                code = name[1].split(']')[0]
                name = name[0]
                branches_data.append([name, code])
            attach = []
            for el in branches_data:
                okved, created = Branch.objects.get_or_create(code=el[1], name=el[0])
                attach.append(okved)
            if organization and attach:
                organization.branch.add(*attach)
        except:
            continue


# from organizations.utils import get_tass
def get_tass():
    path = os.path.join(os.path.dirname(__file__), 'data/excels/gisp.xlsx')
    db = xl.readxl(path)
    ws = db.ws('сводная информация')
    data = list(ws.rows)
    for row in data[2:]:
        if not row[5]:
            continue
        inn = row[18]
        organization = Organization.objects.filter(inn=inn).first()
        tasses = row[5].split('/')
        try:
            tasses_data = []
            for el in tasses:
                name = el.split('[')
                code = name[1].split(']')[0]
                name = name[0]
                tasses_data.append([name, code])
            attach = []
            for el in tasses_data:
                okved, created = Tass.objects.get_or_create(code=el[1], name=el[0])
                attach.append(okved)
            if organization and attach:
                organization.tasses.add(*attach)
        except:
            continue


# from organizations.utils import get_support_measures_data
def get_support_measures_data():  # noqa: C901
    path = os.path.join(os.path.dirname(__file__), 'data/excels/support_measures.csv')
    with open(path, mode='r', encoding="windows-1251") as csv_file:
        line_count = 0
        csv_reader = csv.reader(csv_file, delimiter=';')
        for row in csv_reader:
            print(row[3])
            if line_count == 0:
                line_count += 1
                continue
            else:
                support = SupportMeasures.objects.filter(name=row[3]).first()
                if support:
                    print(row[26])
                    support.is_active = True if row[26] == 'false' else False
                    if row[35]:
                        region, created = Region.objects.get_or_create(region_name=row[35])
                        support.region = region
                    if row[17]:
                        okved_list = []
                        okveds_names = row[17].split(',')
                        for okved_name in okveds_names:
                            okved, created = Okved.objects.get_or_create(name=okved_name)
                            okved_list.append(okved)
                        support.okveds.add(*okved_list)
                    if row[16]:
                        branch_list = []
                        branch_names = row[16].split(',')
                        for branch_name in branch_names:
                            branch, created = Branch.objects.get_or_create(name=branch_name)
                            branch_list.append(branch)
                        support.branch.add(*branch_list)
                    if row[10]:
                        if row[10] == 'Финансовая поддержка':
                            support.support_type = SupportMeasuresTypes.financial
                        elif row[10] == 'Имущественная поддержка':
                            support.support_type = SupportMeasuresTypes.property
                        elif row[10] == 'Консультационная (информационная) поддержка':
                            support.support_type = SupportMeasuresTypes.consulting
                        elif row[10] == 'Образовательная поддержка':
                            support.support_type = SupportMeasuresTypes.educational
                        elif row[10] == 'Поддержка внешнеэкономической деятельности':
                            support.support_type = SupportMeasuresTypes.consulting
                        elif row[10] == ('Регуляторная поддержка '
                                         '(налоговые, таможенные, инвестиционные льготы и т.д.)'):
                            support.support_type = SupportMeasuresTypes.regulator
                    support.save()
                else:
                    support = SupportMeasures.objects.create(name=row[3])
                    support.is_active = True if row[26] == 'false' else False
                    if row[35]:
                        region, created = Region.objects.get_or_create(region_name=row[35])
                        support.region = region
                    if row[17]:
                        okved_list = []
                        okveds_names = row[17].split(',')
                        for okved_name in okveds_names:
                            okved, created = Okved.objects.get_or_create(name=okved_name)
                            okved_list.append(okved)
                        support.okveds.add(*okved_list)
                    if row[16]:
                        branch_list = []
                        branch_names = row[16].split(',')
                        for branch_name in branch_names:
                            branch, created = Branch.objects.get_or_create(name=branch_name)
                            branch_list.append(branch)
                        support.branch.add(*branch_list)
                    if row[10]:
                        if row[10] == 'Финансовая поддержка':
                            support.support_type = SupportMeasuresTypes.financial
                        elif row[10] == 'Имущественная поддержка':
                            support.support_type = SupportMeasuresTypes.property
                        elif row[10] == 'Консультационная (информационная) поддержка':
                            support.support_type = SupportMeasuresTypes.consulting
                        elif row[10] == 'Образовательная поддержка':
                            support.support_type = SupportMeasuresTypes.educational
                        elif row[10] == 'Поддержка внешнеэкономической деятельности':
                            support.support_type = SupportMeasuresTypes.consulting
                        elif row[10] == ('Регуляторная поддержка (налоговые, таможенные, '
                                         'инвестиционные льготы и т.д.)'):
                            support.support_type = SupportMeasuresTypes.regulator
                    support.save()


# from organizations.utils import parse_employ_count
def parse_employ_count():
    path = os.path.join(os.path.dirname(__file__), f'data/xmls/')
    files = os.listdir(path)

    for file_path in files:
        temp_path = os.path.join(path, file_path)
        root = ET.parse(temp_path).getroot()
        documents = root.findall('Документ')
        for document in documents:
            inn = document.find('СведНП').get('ИННЮЛ')
            organization = Organization.objects.filter(inn=inn).first()
            if organization:
                count = int(document.find('СведССЧР').get('КолРаб'))
                if 1 <= count <= 100:
                    size, created = OrganizationSize.objects.get_or_create(name='Малая (1-100 чел.)')
                elif 101 <= count <= 250:
                    size, created = OrganizationSize.objects.get_or_create(name='Средняя(101-250 чел.)')
                else:
                    size, created = OrganizationSize.objects.get_or_create(name='Крупная(251+ чел.)')
                organization.size = size
                organization.save()


# from organizations.utils import parse_naog_regim
def parse_naog_regim():
    path = os.path.join(os.path.dirname(__file__), f'data/xmls_nalog/')
    files = os.listdir(path)

    for file_path in files:
        print(file_path)
        temp_path = os.path.join(path, file_path)
        root = ET.parse(temp_path).getroot()
        documents = root.findall('Документ')
        for document in documents:
            inn = document.find('СведНП').get('ИННЮЛ')
            organization = Organization.objects.filter(inn=inn).first()
            if organization:
                srp = bool(int(document.find('СведСНР').get('ПризнСРП')))
                envd = bool(int(document.find('СведСНР').get('ПризнЕНВД')))
                usn = bool(int(document.find('СведСНР').get('ПризнУСН')))
                eshn = bool(int(document.find('СведСНР').get('ПризнЕСХН')))
                organization.srp = srp
                organization.envd = envd
                organization.usn = usn
                organization.eshn = eshn
                organization.save()
