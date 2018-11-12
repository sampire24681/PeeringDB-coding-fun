This script will do the following:

1- Call peeringDB api Get net_id from AS_no specified

2- Store info from JSON (names,speed,ipv4 and ipv6) + get total speed , total no of peerings ,ixlan ids and arrange them in lists and dictionaries for manipulation and usage  

3- Call API to get ixlan_id info and count peerings + could be used to get the names of peerings as well

4- from the collected info 2 resources will be created : (create an excel workbook and a mongoDB database) 
 
5 -excel workbook showing 4 reports in worksheets
('Total Public Peering'),('Summary Per Exchange'),('Public Peers more info') and ('Total Unique Peering ')
a-'Total Public Peering' : summary report containing (Total number of Exchanges,Total number of Peerings and Total aggregate speed     (Gpbs)) in relation to the specified AS number
b-Summary Per Exchange : summary per exchange; contains: Public Peering exchange,Number of peers per exchange and Aggregate speed per exchange(Gbps)
c-Public Peers more info : more info about peers to the specified AS ; contains: Public Peering Exchange,Speed (Gbps),IPv4,IPv6
d-Total Unique Peering : Summary info from exchanges connected to specified AS; contains : Public Exchange name and Total number of unique peerings

6- Save the same reports on mongo DB Atlas or could be changed to go on local mongo if needed by changing the URI to local connection
a- The database will be checked if data is missing every run to this script and update the collections in case of document loss.


    
