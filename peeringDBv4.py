import json
from collections import defaultdict
import requests
import xlsxwriter
import pymongo




#create db and collection=============================================================
#client = pymongo.MongoClient("mongodb://localhost:27017/")
client = pymongo.MongoClient("mongodb+srv://test:testpass123@cluster0-rzmzf.mongodb.net/test?retryWrites=true")

# create the database 
db = client["peering_db"]   

# create collections
collection1 = db["Total Public Peering"]  
collection2 = db["Summary Per Exchange"]
collection3 = db["Public Peers more info"]
collection4 = db["Total Unique Peering"]



#=================================================================================

#Create Workbook and worksheets + set col size and col titles==============================
workbook = xlsxwriter.Workbook('peeringDB_AS46489.xlsx')
bold = workbook.add_format({'bold': True})
workbook.encoding='utf-8'

worksheet1 = workbook.add_worksheet('Total Public Peering')
worksheet2 = workbook.add_worksheet('Summary Per Exchange')
worksheet3 = workbook.add_worksheet('Public Peers more info')
worksheet4 = workbook.add_worksheet('Total Unique Peering ')

worksheet1.set_column('A:A', 25)
worksheet1.set_column('B:B', 25)
worksheet1.set_column('C:C', 27)


worksheet2.set_column('A:A', 45)
worksheet2.set_column('B:B', 15)
worksheet2.set_column('C:C', 21)

worksheet3.set_column('A:A', 45)
worksheet3.set_column('B:B', 14)
worksheet3.set_column('C:C', 16)
worksheet3.set_column('D:D', 40)

worksheet4.set_column('A:A', 45)
worksheet4.set_column('B:B', 45)

worksheet1.write('A1', 'Total number of Exchanges', bold)
worksheet1.write('B1', 'Total number of Peerings', bold)
worksheet1.write('C1', 'Total aggregate speed (Gpbs)', bold)

worksheet2.write('A1', 'Public Peering exchange', bold)
worksheet2.write('B1', 'Number of peers per exchange', bold)
worksheet2.write('C1', 'Aggregate speed per exchange(Gbps)', bold)

worksheet3.write('A1', 'Public Peering Exchange', bold)
worksheet3.write('B1', 'Speed (Gbps)', bold)
worksheet3.write('C1', 'IPv4', bold)
worksheet3.write('D1', 'IPv6', bold)

worksheet4.write('A1', 'Public Exchange', bold)
worksheet4.write('B1', 'Total number of unique peerings', bold)

#=========================================================================================


def get_API_JSON(obj,value):    #call api according to object and value
    url_object = 'https://peeringdb.com/api/{}/{}'.format(obj,value)
    result_data = requests.get(url_object)
    result_json = result_data.json()
    return result_json   #result_json2 is 2 dictionaries (with keys :meta and data)
                         #each dic contains a list of dictionaries
        

def get_JSON_of_net_id_from_AS(AS_number):# Get net_id from AS_no
    http_object = "https://peeringdb.com/api/net?asn=%s" %AS_number
    result_data = requests.get(http_object)
    result_json1 = result_data.json()
    net_id = result_json1['data'][0]['id']
    result_json2 = get_API_JSON('net',net_id)
    return result_json2


def get_peering_info_from_JSON(result_json2): #store info from JSON (names,speed,ipv4 and ipv6) + get total speed and total no of peerings and exchanges
    name = None
    ipv4_add = None
    ipv6_add = None
    ixlan_id_names ={}
    total_peers = 0
    total_exchanges = 0
    total_speed = 0
    name_speed_dic = defaultdict(list)
    name_speed_ipv4_ipv6_lst = []

    for pop in result_json2['data'][0]['netixlan_set']:
        name_speed_ipv4_ipv6_lst.append([pop['name'],pop['speed']/1000.0,pop['ipaddr4'],pop['ipaddr6']]) #build lst of lsts (name,speed,ipv4 and ipv6)
        name_speed_dic[pop['name']].append(pop['speed'])   #build separate dic for name_speed to get a per exchange summary view (number of peers and agg speed)
        ixlan_id_names[pop['ixlan_id']] = pop['name']    #build dic ixlan_id vs name to use later to get details of ixids and to get the total unique peers
        total_peers+= 1
        total_speed += pop['speed'] /1000.0


    name_speed_ipv4_ipv6_lst.sort()    
  

    for key,value in ixlan_id_names.items():  # get total number of exchanges from ixlan_names dic
        total_exchanges+=1

    total_lst= [total_exchanges,total_peers,total_speed]
    
    return  ixlan_id_names,name_speed_ipv4_ipv6_lst,name_speed_dic,total_lst




def get_unique_peering(ixlan_id_names):  #Take ixlan_id and count peerings + could be used to get the names of peerings as well
    uniq_pop_dic = defaultdict(list)
    name_total_unique_peering = {}
    
    for ixlan_id,name in ixlan_id_names.items():
        total_unique_peering_count = 0
        result_json3 = get_API_JSON('ixlan',ixlan_id)     # fnc translates to get https://peeringdb.com/api/ixlan/<ixlan_id>
        
        total_unique_peering_count = len(result_json3['data'][0]['net_set'])
        
        name_total_unique_peering[name] = total_unique_peering_count

    return uniq_pop_dic , name_total_unique_peering    #return 2 dictionaries ,1 for unique pop with all peers and the other the unique peer and the number of peerings)


def get_name_numberofpeers_aggspeed_from(name_speed_dic): 
    name_numberofpeers_aggspeed_lst = []
    
    for key, item in name_speed_dic.items():
        aggspeed_gbps = sum(item) /1000.0 
        name_numberofpeers_aggspeed_lst.append([key,len(name_speed_dic[key]),aggspeed_gbps] )
    name_numberofpeers_aggspeed_lst.sort()
    return name_numberofpeers_aggspeed_lst




def depthCount(lst):#takes a nested list as a parameter and returns the maximum depth to which the list has nested sub-lists.'
                    # to determine how many colums to account for when building table

    if isinstance(lst, list):
        return 1 + max(depthCount(x) for x in lst)
    else:
        return 0
        

def build_tables_xlsx(worksheet_number,lst):   # build xlsx tables
    if depthCount(lst) == 1:
        row_index = 0
        for col_index in range(len(lst)):
            worksheet_number.write(row_index+1, col_index, lst[col_index])           
    if depthCount(lst) == 2:
        for row_index in range(0 , len(lst)):
            for col_index in range(len(lst[0])):
                worksheet_number.write(row_index+1, col_index, lst[row_index][col_index] )
                  

#=============================================================================================

print "Public peerings :- Collecting net_ids and querying exchanges peering with  AS46489..."
result_json2 = get_JSON_of_net_id_from_AS("46489")

ixlan_id_names,name_speed_ipv4_ipv6_lst,name_speed_dic,total_lst = get_peering_info_from_JSON(result_json2)
name_numberofpeers_aggspeed_lst = get_name_numberofpeers_aggspeed_from(name_speed_dic)
print "[Collection complete]\n\n"


print "Unique peerings:- querying total number of peers for each exchange peering with AS46489. This operation may take 1-2 minutes to complete, please wait..."
uniq_pop_dic , name_total_unique_peering = get_unique_peering(ixlan_id_names)
name_total_unique_peering_lst = []
for key,item in name_total_unique_peering.items():
    name_total_unique_peering_lst.append([key,item])    
name_total_unique_peering_lst.sort()
print "[Collection complete]\n\n"

#============================================================================================

print "Building xlsx worksheets"
#build xlsx tables from extracted lists  and close to save   
build_tables_xlsx(worksheet1,total_lst)
build_tables_xlsx(worksheet2,name_numberofpeers_aggspeed_lst)
build_tables_xlsx(worksheet3,name_speed_ipv4_ipv6_lst)
build_tables_xlsx(worksheet4,name_total_unique_peering_lst)
workbook.close()
print "[Worksheets are created successfully]\n\n"



#build mongoDB collections in peeringDB database
#===============================================
#check if same _id exist in collection,add if new or update if yes.
print "Building database collections"
total_lst_mongo={'_id': "Total Report",
                    "Total number of Exchanges":total_lst[0],
                    "Total number of Peerings":total_lst[1],
                    "Total aggregate speed (Gpbs)":total_lst[2]}

collection1.update_one({'_id':"Total Report"}, {"$set": total_lst_mongo}, upsert=True)

 
#insert collection2 (transfer from listoflists:name_numberofpeers_aggspeed_lst)
for index,i in enumerate(name_numberofpeers_aggspeed_lst):
    name_numberofpeers_aggspeed_lst_mongo ={'_id':name_numberofpeers_aggspeed_lst[index][0],
                                            'Number of peers per exchange':name_numberofpeers_aggspeed_lst[index][1],
                                            'Aggregate speed per exchange(Gbps)':name_numberofpeers_aggspeed_lst[index][2]}
    
    collection2.update_one({'_id':name_numberofpeers_aggspeed_lst[index][0]},
                           {"$set": name_numberofpeers_aggspeed_lst_mongo},upsert=True)


#insert collection3 (transfer from listoflists:name_speed_ipv4_ipv6_lst)    
for index,i in enumerate(name_speed_ipv4_ipv6_lst):
    name_speed_ipv4_ipv6_lst_mongo ={'_id': name_speed_ipv4_ipv6_lst[index][0]+"_"+str(index+1),   #to make id unique as exchange id could duplicate due to more than 1 peering
                                     'Speed (Gbps)':name_speed_ipv4_ipv6_lst[index][1],
                                     'IPv4':name_speed_ipv4_ipv6_lst[index][2],
                                     'IPv6':name_speed_ipv4_ipv6_lst[index][3]}
    collection3.update_one({'_id': name_speed_ipv4_ipv6_lst[index][0]+"_"+str(index+1)},
                           {"$set": name_speed_ipv4_ipv6_lst_mongo}, upsert=True)



#insert collection4 (transfer from listoflists:name_total_unique_peering_lst)
for index,i in enumerate(name_total_unique_peering_lst):
    name_total_unique_peering_lst_mongo ={'_id':name_total_unique_peering_lst[index][0]+"_"+str(index+1),
                                          'Total number of unique peerings':name_total_unique_peering_lst[index][1]}
    collection4.update_one({'_id':name_total_unique_peering_lst[index][0]+"_"+str(index+1)},
                           {"$set": name_total_unique_peering_lst_mongo},upsert=True)


print "[Database/collections are saved/updated successfully]/nPlease check outputs now!\n\n"



