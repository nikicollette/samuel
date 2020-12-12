import requests
import json
import pandas as pd
import streamlit as st
import datetime
import matplotlib.pyplot as plt

st.title("Samuel")
st.markdown("US Securities Dashboard")

gsid_options = st.multiselect('Select the companies that you  would like to compare (gsid)', ['10516', '10696', '11308', '11896', '13901', '13936', '14593', '148401', '149756', '150407', '15579', '173578', '12490', '176665', '177256', '17750', '85072', '183269', '183414', '151048', '18729', '188329', '188804', '193155', '193324', '198025', '152963', '161467', '213305', '216587', '216722', '217708', '22293', '222946', '223416', '16432', '16600', '227284', '230958', '25022', '26403', '26825', '29209', '172890', '18163', '46886', '40539', '44644', '46578', '46922', '49154', '53065', '53613','55976','59010','59248','61621','64064','66384','69796','70500','75100','75154','75573','75607','76226','76605','193067','77659','78045','78975','79145','79265','79758','80286','80791','81116','82598','194688','84275','197235','84769','905255','85517','85627','85631','85914','86196','86356','86372','202271','901237','226278','902608','902704','903917','905288','905632','91556', '16678'])

st.markdown("Select the start date and end date between 2012-07-01 to 2017-06-30")
start_date_datetime = st.date_input('start date', datetime.date(2012,1,7))
end_date_datetime = st.date_input('end date', datetime.date(2017,6,30))

auth_data = {
    "grant_type"    : "client_credentials",
    "client_id"     : "93c09f2e3a6e4150b50334f2ead49ab2",
    "client_secret" : "796002fd7ad95eaafac28c0669afd0274df67a60ad5cc09db4dd813c0c88c56a",
    "scope"         : "read_product_data"
}

# create session instance
session = requests.Session()

auth_request = session.post("https://idfs.gs.com/as/token.oauth2", data = auth_data)
access_token_dict = json.loads(auth_request.text)
access_token = "0012NkJpYOmEGZmibnTl8qH6ubI4"

# update session headers with access token
session.headers.update({"Authorization":"Bearer "+ access_token})

request_url = "https://api.marquee.gs.com/v1/data/USCANFPP_MINI/query"


start_date = start_date_datetime.strftime("%Y-%m-%d")
end_date = end_date_datetime.strftime("%Y-%m-%d")

if (gsid_options != [] ):
    if ("all" in gsid_options):
        request_query = {
                        "startDate": start_date,
                        "endDate": end_date
        }

    else:
        request_query = {
                            "where": {
                                "gsid": gsid_options},
                            "startDate": start_date,
                            "endDate": end_date
        }

    request = session.post(url=request_url, json=request_query)
    results = json.loads(request.text)
    results = json.loads(request.text)
    results = pd.DataFrame(results)
    results["date"] = results["data"]
    results["gsid"] = results["data"]
    results["financialReturnsScore"] = results["data"]
    results["growthScore"] = results["data"]
    results["multipleScore"] = results["data"]
    results["integratedScore"] = results["data"]
    results["updateTime"] = results["data"]
    counter = 0
    for result in results["data"]:
        results["date"][counter] = result.get('date')
        results["gsid"][counter] = result.get('gsid')
        results["financialReturnsScore"][counter] = result.get('financialReturnsScore')
        results["growthScore"][counter] = result.get('growthScore')
        results["multipleScore"][counter] = result.get('multipleScore')
        results["integratedScore"][counter] = result.get('integratedScore')
        results["updateTime"][counter] = result.get('updateTime')
        counter += 1

    results = results.drop('data', 1)

    #add here - sneha
    st.write("graphs")

    st.markdown("Select a date between your start date and end date to analyze")
    compare_date = st.date_input('date', start_date_datetime)
    if (compare_date > end_date_datetime or compare_date < start_date_datetime) :
        st.write("Please enter a date that is between your start date and end date")
    else :


        def financialReturnandGrowthScore():
          #Allow users to input list of company id and the date
          #Weight values
          financialReturnWeight = st.number_input("Enter the weight for financialScore (0 -100)", 0, 100,0, 1)
          growthWeight  = st.number_input("Enter the weight for growthScore (0 -100)",  0, 100, 0, 1)
          companies = []
          companyID = gsid_options
          date = compare_date.strftime("%Y-%m-%d")
          for i in range(len(gsid_options)):
              temp = results.loc[results["gsid"] == gsid_options[i]]
              temp = temp.loc[temp["date"] == date]
              if (temp is None):
                  st.write("the date doesn't work")
              else:
                  value1 = temp['financialReturnsScore'].iloc[0]
                  value2 = temp['financialReturnsScore'].iloc[0]
                  companyID[i]= {
                      "name": gsid_options[i],
                      "Date": compare_date,
                      "WeightedFinancialReturn": float(0 if value1 is None else value1)*float(financialReturnWeight),
                      "WeightedGrowthScore": float(0 if value2 is None else value2)*float(growthWeight)
                  }
                  companies.append(companyID[i])

          return pd.DataFrame(companies)


        def percentageChange():
          data = financialReturnandGrowthScore()
          data['FinancialReturn%Change'] = (data['WeightedFinancialReturn'] / data['WeightedFinancialReturn'].sum()) * 100
          data['GrowthScore%Change'] = (data['WeightedGrowthScore'] / data['WeightedGrowthScore'].sum()) * 100
          data['Ranks'] = (data['WeightedGrowthScore'] + data['WeightedFinancialReturn']).rank(ascending = 0)
          data.head(10)
          return data

        def visualize():
          data = percentageChange()
          #Financial Return plot
          fig, ax = plt.subplots(figsize = (10,10))
          wedges,_,_ = ax.pie(data['FinancialReturn%Change']
                              ,labels=data["name"]
                              ,shadow=False,startangle=90, autopct="%1.1f%%"
                              ,textprops={'fontsize': 16})
          ax.legend(wedges,data["name"], loc="upper center", prop={'size': 16});
          ax.set_title("Financial Return Ranking")
          st.pyplot(fig)

          #Growth score plot
          fig, ax = plt.subplots(figsize = (10,10))
          wedges,_,_ = ax.pie(data['GrowthScore%Change']
                              ,labels=data["name"]
                              ,shadow=False,startangle=90, autopct="%1.1f%%"
                              ,textprops={'fontsize': 16})
          ax.legend(wedges,data["name"], loc="upper center", prop={'size': 16});
          ax.set_title("Growth Score Ranking")
          st.pyplot(fig)

          # Overall ranking
          fig, ax = plt.subplots(figsize = (10,10))
          wedges,_,_ = ax.pie(data['Ranks']
                              ,labels=data["name"]
                              ,shadow=False,startangle=90, autopct="%1.1f%%"
                              ,textprops={'fontsize': 16})
          ax.legend(wedges,data["name"], loc="upper center", prop={'size': 16});
          ax.set_title("Overall Ranking")
          st.pyplot(fig)

        finalResult = visualize()


    # results = pd.DataFrame(results)
