from datetime import datetime, timedelta, time
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import streamlit as st
import pandas as pd
import requests
import pickle

T2 = datetime.now()

st.set_page_config(layout="wide")

github_session = requests.Session()
github_session.auth = ('Zech123as', "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")

ST_Form = st.sidebar.form("St_form")

Max_Profit = j = 0

Index_Name = ST_Form.radio("Select Index", ("NIFTY BANK", "NIFTY 50"))
Expiry_Dist_input = ST_Form.slider("Select Expiry Distance", min_value = 0, max_value = 40, value = (2,2))

Entry_Date, Exit_Date = ST_Form.select_slider("Entry & Exit Date Inputs", options = [datetime(2010, 1, 1), datetime(2010, 1, 4), datetime(2010, 1, 5), datetime(2010, 1, 6), datetime(2010, 1, 7)], value = (datetime(2010, 1, 1),datetime(2010, 1, 7)), format_func = lambda x: x.strftime("%A"))
Time_Input = ST_Form.slider("Entry & Exit Time Inputs", min_value = time(9, 15), max_value = time(15, 30), value = (time(9, 30), time(15, 30)), step = timedelta(minutes = 15))

Sell_Dist_input = ST_Form.slider("Sell Distance", min_value = -15, max_value = 40, value = (-10, -10))

Buy_Lots  = ST_Form.slider("No of Buy Lots", min_value = 0, max_value = 15, value = 5)
Buy_Dist  = ST_Form.slider("Buy Distance", min_value = 0, max_value = 30, value = 15)

ST_Form.form_submit_button("Submit")


if Index_Name == "NIFTY 50":
	Index_Dist, Lot_Size = 50, 50
elif Index_Name == "NIFTY BANK":
	Index_Dist, Lot_Size = 100, 25
else:
	print("Incorrect Index Name")

end_time_input_base = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

while end_time_input_base.strftime("%A") != "Thursday":
	end_time_input_base = end_time_input_base - timedelta(days = 1)

fig_dict = {}

for Sell_Dist in range((Sell_Dist_input)[0], (Sell_Dist_input)[1]+1, 1):
	
	fig_dict.update({Sell_Dist : go.Figure()})
	
	k = 0
	
	while Entry_Date + timedelta(days = k) != Exit_Date:
		Date_Divider = Entry_Date + timedelta(days=k+1, hours=9, minutes=7)
		fig_dict[Sell_Dist].add_vline(x= Date_Divider, line_width=0.7, line_dash="solid", line_color="#bab6b6")
		k = k + 1

for Expiry_Dist in range(Expiry_Dist_input[0], Expiry_Dist_input[1] + 1, 1):
	
	end_time_input = end_time_input_base - timedelta(days = Expiry_Dist*7)
	
	if end_time_input == datetime(2021, 11, 4):
		end_time_input = end_time_input
	elif True:
		
		try:
			Data = pickle.loads(github_session.get(f"https://raw.githubusercontent.com/Zech123as/One/main/Expiry_Data/Expiry_Dict_{end_time_input.date()}.pkl").content)
		except:
			break
		
		Main_Dict = Data[Index_Name]
		
		
		Index_csv_1 = (Main_Dict["Index_csv_1"]).copy()

		Index_csv_1["time"] = Index_csv_1["time"] - (end_time_input - datetime(2010,1,7))
		
		Entry_Time = timedelta( hours=list(Time_Input)[0].hour, minutes = list(Time_Input)[0].minute )
		Exit_Time  = timedelta( hours=list(Time_Input)[1].hour, minutes = list(Time_Input)[1].minute )

		Index_csv_2 = Main_Dict["Index_csv_2"].copy()
		
		Index_csv_2.index = Index_csv_2.index - (end_time_input - datetime(2010,1,7))

		Index_csv_2 = Index_csv_2.reindex(pd.date_range(Entry_Date + Entry_Time, Exit_Date + Exit_Time, freq = '1min')).between_time('09:16','15:30')	

		Index_csv_2['c'] = Index_csv_2['c'].ffill().bfill()
		Index_csv_2['o'].fillna(Index_csv_2['c'], inplace=True)



		Index_Entry = Index_csv_2.o[Entry_Date + Entry_Time]
		Index_Exit  = Index_csv_2.o[Exit_Date  + Exit_Time ]

		Index_Range_Min, Index_Range_Max = int((Index_csv_2["o"].min()/100)-1)*100, int((Index_csv_2["o"].max()/100)+2)*100

		Index_Range = int(Index_csv_2["o"].max() - Index_csv_2["o"].min())

		ce_atm = (round(Index_csv_2.o[Entry_Date + Entry_Time]//Index_Dist)-0)*Index_Dist
		pe_atm = (round(Index_csv_2.o[Entry_Date + Entry_Time]//Index_Dist)+1)*Index_Dist


		for Sell_Dist in range((Sell_Dist_input)[0], (Sell_Dist_input)[1]+1, 1):

			ce_sell_dist, pe_sell_dist = Sell_Dist, -Sell_Dist

			ce_sell = Main_Dict[str(ce_atm + ce_sell_dist*Index_Dist) + 'CE'].copy()
			pe_sell = Main_Dict[str(pe_atm + pe_sell_dist*Index_Dist) + 'PE'].copy()

			ce_sell.index = ce_sell.index - (end_time_input - datetime(2010,1,7))
			pe_sell.index = pe_sell.index - (end_time_input - datetime(2010,1,7))

			ce_sell = ce_sell.reindex(pd.date_range(Entry_Date + Entry_Time, Exit_Date + Exit_Time, freq = '1min')).between_time('09:16','15:30')
			pe_sell = pe_sell.reindex(pd.date_range(Entry_Date + Entry_Time, Exit_Date + Exit_Time, freq = '1min')).between_time('09:16','15:30')
			
			ce_sell['c'] = ce_sell['c'].ffill().bfill()
			pe_sell['c'] = pe_sell['c'].ffill().bfill()

			ce_sell['o'].fillna(ce_sell['c'], inplace=True)
			pe_sell['o'].fillna(pe_sell['c'], inplace=True)

			ce_sell_entry, pe_sell_entry = ce_sell.o[Entry_Date + Entry_Time], pe_sell.o[Entry_Date + Entry_Time]
			ce_sell_exit , pe_sell_exit  = ce_sell.o[Exit_Date + Exit_Time]  , pe_sell.o[Exit_Date + Exit_Time]


			ce_buy_dist, pe_buy_dist = Sell_Dist + Buy_Dist, -Sell_Dist-Buy_Dist

			ce_buy = Main_Dict[str(ce_atm + ce_buy_dist*Index_Dist) + 'CE'].copy()
			pe_buy = Main_Dict[str(pe_atm + pe_buy_dist*Index_Dist) + 'PE'].copy()

			ce_buy.index = ce_buy.index - (end_time_input - datetime(2010,1,7))
			pe_buy.index = pe_buy.index - (end_time_input - datetime(2010,1,7))

			ce_buy = ce_buy.reindex(pd.date_range(Entry_Date + Entry_Time, Exit_Date + Exit_Time, freq = '1min')).between_time('09:16','15:30')
			pe_buy = pe_buy.reindex(pd.date_range(Entry_Date + Entry_Time, Exit_Date + Exit_Time, freq = '1min')).between_time('09:16','15:30')

			ce_buy['c'] = ce_buy['c'].ffill().bfill()
			pe_buy['c'] = pe_buy['c'].ffill().bfill()

			ce_buy['o'].fillna(ce_buy['c'], inplace=True)
			pe_buy['o'].fillna(pe_buy['c'], inplace=True)

			ce_buy_entry, pe_buy_entry = ce_buy.o[Entry_Date + Entry_Time], pe_buy.o[Entry_Date + Entry_Time]
			ce_buy_exit , pe_buy_exit  = ce_buy.o[Exit_Date + Exit_Time]  , pe_buy.o[Exit_Date + Exit_Time]

			Final_DF = pd.DataFrame()

			Final_DF['Change' + str(Sell_Dist)] = ((ce_sell_entry + pe_sell_entry) - (ce_sell['o'] + pe_sell['o'])) + (((ce_buy['o'] + pe_buy['o']) - (ce_buy_entry + pe_buy_entry))*Buy_Lots)

			Final_DF["CE_SELL"] = "CE (" + str(round(ce_sell_entry)).rjust(5) + " |" + ce_sell['o'].round().astype(int).astype(str).str.rjust(5) + " )"
			Final_DF["PE_SELL"] = "PE (" + str(round(pe_sell_entry)).rjust(5) + " |" + pe_sell['o'].round().astype(int).astype(str).str.rjust(5) + " )"

			Final_DF["CE_BUY"]  = "CE (" + str(round(ce_buy_entry)).rjust(5) + " |" + ce_buy['o'].round().astype(int).astype(str).str.rjust(5) + " )"
			Final_DF["PE_BUY"]  = "PE (" + str(round(pe_buy_entry)).rjust(5) + " |" + pe_buy['o'].round().astype(int).astype(str).str.rjust(5) + " )"	

			Final_DF["FINAL 1"] = "CE" + Final_DF["CE_SELL"] + "   |   " + Final_DF["CE_BUY"]
			Final_DF["FINAL 2"] = "PE" + Final_DF["PE_SELL"] + "   |   " + Final_DF["PE_BUY"] + " * " + str(Buy_Lots)
			
			if Final_DF['Change' + str(Sell_Dist)].max() > Max_Profit:
				Max_Profit = Final_DF['Change' + str(Sell_Dist)].max()

			if Index_Range in range(0, 1001):
				Legend_Group = "0 - 1000"
				Group_Rank = 1
			elif Index_Range in range(1001, 1501):
				Legend_Group = "1000 - 1500"
				Group_Rank = 2
			elif Index_Range > 1500:
				Legend_Group = "> 1500"
				Group_Rank = 3

			fig_dict[Sell_Dist].add_trace(go.Scatter(x=Final_DF.index, y=Final_DF["Change"+str(Sell_Dist)], legendrank = Group_Rank, mode = 'lines', legendgrouptitle_text = Legend_Group, legendgroup= Legend_Group, customdata = Final_DF, name = str(end_time_input.date()).rjust(10), hovertemplate='Profit: (%{y:5d} )   |   %{customdata[1]}<br>%{customdata[2]}'))


for Sell_Dist in range((Sell_Dist_input)[0], (Sell_Dist_input)[1]+1, 1):

	fig_dict[Sell_Dist].update_xaxes(showspikes=True, spikedash = "solid", spikecolor="red", spikesnap="hovered data", spikemode="across", spikethickness = 0.5)
	fig_dict[Sell_Dist].update_xaxes(rangebreaks=[dict(bounds=[15.75, 9], pattern="hour")])
	fig_dict[Sell_Dist].update_xaxes(rangeslider_visible=True)
	fig_dict[Sell_Dist].update_xaxes(showgrid=False)
	
	fig_dict[Sell_Dist].update_yaxes(showgrid=True, gridcolor='#e0e0e0', zerolinecolor = '#989c9b')
	
	fig_dict[Sell_Dist].update_layout(title = Sell_Dist, height = 900, hovermode = "x")
	
	st.plotly_chart(fig_dict[Sell_Dist], use_container_width = True, config={'displayModeBar': True})

(datetime.now() - T2)
