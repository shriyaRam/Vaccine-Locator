import PySimpleGUI as sg
import os.path
import requests
import webbrowser
import datetime
import json
import os


def getApiUrl(tab):
    urlPin = 'https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/findByPin'
    urlDistrict = 'https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/findByDistrict'

def apiCall(district_id, date):
    query = {'district_id':district_id, 'date':date}
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36', 'Accept-Language' : 'en-US'}
    response = requests.get('https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/findByDistrict', params=query, headers=headers)
    return response

def apiCallPIN(pin, date):
    query = {'pincode':str(pin), 'date':date}
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36', 'Accept-Language' : 'en-US', 'accept': 'application/json'}
    response = requests.get('https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/findByPin', params=query, headers=headers)
    return response

def determineSearchArea(area):
    if area=='Thane':
        return ['392']
    elif area == 'Mumbai':
        return ['395']
    else:
        return ['392', '395'] 

def filterResponse(response, vaccine, dose, age, district, fee_type):
    c=1
    msgs=[]
    for i in range(0, len(response.json().get('sessions'))):
        if response.json().get('sessions')[i]['vaccine'] == vaccine and response.json().get('sessions')[i][dose] > 0 and response.json().get('sessions')[i]['min_age_limit']==age and response.json().get('sessions')[i]['fee_type']==fee_type:
            msgs.append(str(c)+".\nCenter:\n"+response.json().get('sessions')[i]['name']+"\n"+"Address:\n"+response.json().get('sessions')[i]['address']+"\n"+"Doses left: "+str(response.json().get('sessions')[i][dose])+"\n"+"PINCODE: "+str(response.json().get('sessions')[i]['pincode'])+"\n"+"Fee: "+response.json().get('sessions')[i]['fee'])
            c = c+1 
    if(c==1):
        msgs.append(vaccine+" not available in Thane" if (district=="392") else vaccine+" not available in Mumbai")
        return "\n".join(msgs)
    else:
        return "\n".join(msgs)

def filterResponsePIN(response, vaccine, dose, age, pin, fee_type):
    c=1
    msgs=[]
    #print(response)
    for i in range(0, len(response.json().get('sessions'))):
        if response.json().get('sessions')[i]['vaccine'] == vaccine and response.json().get('sessions')[i][dose] > 0 and response.json().get('sessions')[i]['min_age_limit']==age and response.json().get('sessions')[i]['fee_type']==fee_type:
            msgs.append(str(c)+".\nCenter:\n"+response.json().get('sessions')[i]['name']+"\n"+"Address:\n"+response.json().get('sessions')[i]['address']+"\n"+"Doses left: "+str(response.json().get('sessions')[i][dose])+"\n"+"PINCODE: "+str(response.json().get('sessions')[i]['pincode'])+"\n"+"Fee: "+response.json().get('sessions')[i]['fee'])
            c = c+1 
    if(c>1):
        return "\n".join(msgs)
    return ""

def outputWindow(result):
    font = ('Courier New', 16)
    column = [[sg.Text(result, font=font)]]
    layout = [
        [sg.Column(column, size=(800, 300), scrollable=True, key = "Column")],
        [sg.Button('Book on Cowin'), sg.Button('Up', key = "up"), sg.Button('Down', key = "down")],
    ]

    window = sg.Window('Search Results', layout, finalize=True)

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            break
        elif event == 'Book on Cowin':
            webbrowser.open("https://www.cowin.gov.in/home")
        elif event == "down":
            window['Column'].Widget.canvas.yview_moveto(1.0)
        elif event == "up":
            window['Column'].Widget.canvas.yview_moveto(0.0)

def printResults(msgs):
    result=''
    for msg in msgs:
        result = result + msg + "\n"
    if result == '':
        outputWindow('Vaccine not available for the given search')
    else:
        outputWindow(result)

def main():
    layoutDistrict = [[sg.Text("AGE: ",size =(15, 1)),sg.Radio('18+','AGE', default = False, key='Age'),sg.Radio('45+','AGE', default = False)],
            [sg.Text("AREA: ",size =(15, 1)),sg.Combo(['Thane', 'Mumbai', 'Both'], default_value='Select area', key='Area', size=(20,10))],
            [sg.Text("DOSE: ",size =(15, 1)),sg.Radio('Dose 1','dose', default = False, key='dose'),sg.Radio('Dose 2','dose', default = True)],
            [sg.Text("FEE TYPE: ",size =(15, 1)),sg.Radio('Free','fee_type', default = False, key='fee_type'),sg.Radio('Paid','fee_type', default = True)],
            [sg.Text("DATE: ",size =(15, 1)),sg.In(size=(20,10),background_color='white', key='Date'),sg.CalendarButton(button_text = '>',format='%d-%m-%Y')],
            [sg.Text("VACCINE: ",size =(15, 1)),sg.Combo(['COVAXIN', 'COVISHIELD'], default_value='COVAXIN', key='vax', size=(20,10))],
            [sg.Button("Find"), sg.Cancel()]]
    
    layoutPIN = [
            [sg.Text("AGE: ",size =(15, 1)),sg.Radio('18+','AGE', default = False, key='AgePIN'),sg.Radio('45+','AGE', default = False)],
            [sg.Text("PINCODE: ",size =(15, 1)),sg.In(key='StartPIN', size=(20,10)),sg.Text(" - "),sg.In(key='EndPIN', size=(20,10))],
            [sg.Text("DOSE: ",size =(15, 1)),sg.Radio('Dose 1','dose', default = False, key='dosePIN'),sg.Radio('Dose 2','dose', default = True)],
            [sg.Text("FEE TYPE: ",size =(15, 1)),sg.Radio('Free','fee_type', default = False, key='fee_typePIN'),sg.Radio('Paid','fee_type', default = True)],
            [sg.Text("DATE: ",size =(15, 1)),sg.In(size=(20,10),background_color='white', key='DatePIN'),sg.CalendarButton(button_text = '>',format='%d-%m-%Y')],
            [sg.Text("VACCINE: ",size =(15, 1)),sg.Combo(['COVAXIN', 'COVISHIELD'], default_value='COVAXIN', key='vaxPIN', size=(20,10))],
            [sg.Button("Search"), sg.Cancel()]
            ]

    tabgroup = [
                    [
                        sg.TabGroup(
                            [
                                [sg.Tab('By District', layoutDistrict, tooltip='tip', key = 'distTab'), sg.Tab('By PIN', layoutPIN, key = 'pinTab')]
                            ]
                        ,tooltip='pin2')
                    ]
                ]

    window = sg.Window(title="Vaccinator",layout = tabgroup,default_element_size=(200, 50))

    while True:
        event, values = window.read()
        print(values)
        if  event == "Find":
            #initialise values
            district_id = determineSearchArea(values['Area'])
            vaccine = values['vax']
            date = values['Date']
            dose = 'available_capacity_dose1' if (values['dose']==True) else 'available_capacity_dose2'
            fee_type = 'Free' if (values['fee_type']==True) else 'Paid'
            age = 18 if (values['Age']==True) else 45
            msg=[]
            #make API calls
            for district in district_id:
                response = apiCall(district, date)
                msg.append(filterResponse(response, vaccine, dose, age, district, fee_type))
                msg.append("\n")
            printResults(msg)

        if  event == "Search":
            #initialise values
            startPIN = int(values['StartPIN'])
            endPIN = int(values['EndPIN'])
            vaccine = values['vaxPIN']
            date = values['DatePIN']
            dose = 'available_capacity_dose1' if (values['dosePIN']==True) else 'available_capacity_dose2'
            fee_type = 'Free' if (values['fee_typePIN']==True) else 'Paid'
            age = 18 if (values['AgePIN']==True) else 45
            msg=[]
            #make API calls
            for pin in range(startPIN, endPIN+1):
                response = apiCallPIN(pin, date)
                filtered = filterResponsePIN(response, vaccine, dose, age, pin, fee_type)
                if filtered!='':
                    msg.append(filtered)
                    msg.append("\n")
            printResults(msg)
                
        if event == sg.WIN_CLOSED or event == 'Cancel':
            break
    window.close()
if __name__ == "__main__": 
    main()

    

