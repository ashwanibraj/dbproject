from django.shortcuts import render, redirect
from django.utils import timezone
from django.db import transaction
from django.db import models
from finapp.models import UsersDetails, CustomerTransactions, CompanyDetails, CompanyFinance
from finapp.models import SegmentDetails, SharesDetails, CustomerAccounts, SharesHistory
from finapp.forms import loginForm, signupForm, buysellForm, reportsearchForm, brokerageupdForm, tuplecountForm
from finapp.forms import compsearchForm, sectorsearchForm, acctForm, histForm, repselectForm, adminrepForm
from finapp.forms import transTable, histTable, resTable, emptyTable, segcompTable, adminrep1Table, adminrep2Table
from finapp.forms import res2Table, res3Table, hniTable, adminrep3Table, adminrep4Table
from django.db import connection
from datetime import datetime
from django_tables2 import RequestConfig

global_uid = 0
# Create your views here.
def signin(request):
	form = loginForm()	
	msg = ''
	if request.method == 'POST':
		form = loginForm(request.POST)
		if form.is_valid():
			username=form.cleaned_data["username"]
			password=form.cleaned_data["password"]
			cursor = connection.cursor()
			cursor.execute("SELECT user_id FROM Users_Details WHERE username = %s AND password = %s", (username, password))
			val = cursor.fetchone()
			cnt = cursor.rowcount			
			if val == None:				
				msg = "Username and password do not match. Try again."
				cursor.close()
				context = { 'form' : form, 'msg' : msg }
				return render(request, 'finapp/signin.html', context)
			else:
				global global_uid
				global_uid = val[0]
				#msg = 'Val', val, global_uid
				#context = { 'form' : form, 'msg' : msg }
				#return render(request, 'finapp/signin.html', context)
				a=1
				cursor.execute("UPDATE Users_Details SET current_login_time = SYSDATE WHERE user_id = %s AND 1=%s", (global_uid, a))
				cursor.close()
				request.session['uid'] = val[0]
    			return redirect('/finapp/home/')
	context = { 'form' : form, 'msg' : msg }
	return render(request, 'finapp/signin.html', context)

def signup(request):
	form = signupForm()
	msg = ''
	if request.method == 'POST':
		form = signupForm(request.POST)
		if form.is_valid():
			username=form.cleaned_data["username"]			
			
			val = UsersDetails.objects.raw('SELECT user_id FROM Users_Details WHERE username = %s', 
											[username])
			if len(list(val)) == 0:			
				confirm_password = form.cleaned_data["confirm_password"]	
				password = form.cleaned_data["password"]
				if confirm_password == password:				
					first_name = form.cleaned_data["first_name"]
					last_name = form.cleaned_data["last_name"]				
					gender = form.cleaned_data["gender"]
					age = form.cleaned_data["age"]
					
					cursor = connection.cursor()

					cursor.execute("""INSERT INTO Users_Details 
											 VALUES (user_id_seq.NEXTVAL, 
											 		100, %s, %s, %s, %s, %s, 
											 		SYSDATE, NULL, NULL, %s, 
											 		NULL, NULL, (SELECT user_brokerage_pct 
											 						FROM user_roles 
											 						WHERE role_id = 100))""", 
									(username, 
									first_name, 
									last_name,
									gender,
									age,
									password))

					
					#user_id = UsersDetails.objects.raw('SELECT user_id FROM Users_Details WHERE username = %s', [username])[0]
					cursor.execute("""INSERT INTO Customer_Accounts 
											VALUES (account_id_seq.NEXTVAL, user_id_seq.CURRVAL, 10000, 10000)""")

					msg = 'Successfully registered.'
					cursor.execute("commit")
					cursor.close()
					#HttpResponseRedirect('/blog/home/%s' %(user.get_username()))
				else:
					msg = ('Confirm Password did not match. Try again.')
			else:
				msg = "Username already exists. Please choose a different one."
	context = { 'form' : form, 'msg' : msg }
	return render(request, 'finapp/signup.html', context)

def home(request):	
	a=1
	tbl_msg = ''
	uid = request.session.get('uid')	
	cursor = connection.cursor()
	cursor.execute("""SELECT first_name||' '||last_name AS full_name, (SELECT role_name 
																		FROM user_roles 
																		WHERE role_id = ud.role_id) role_name
												FROM Users_Details ud WHERE user_id = %s AND 1=%s""",
					(uid,
					a))
	usr = cursor.fetchone()
	full_name = usr[0]	
	role_name = usr[1]
	request.session['full_name'] = full_name

	cursor.execute("SELECT last_login_time, NVL(ROUND(total_loggedin_mins,2),0) FROM Users_Details WHERE user_id = %s AND 1=%s",
					(uid,
					a))
	temp = cursor.fetchone()
	last_login_time = temp[0]
	total_loggedin_time = temp[1]

	if last_login_time == None:
		last_login_time = 'Right Now (New User)'

	trans_set = CustomerTransactions.objects.raw("""SELECT trans_id,
  					(SELECT share_code FROM shares_details WHERE share_id = ct.share_id
  					) share_code,
  					no_of_shares,
			  		trans_type,
  					ROUND(amount, 2) amount,
  					trans_date
					FROM customer_transactions ct
					WHERE user_id = %s
					ORDER BY trans_date desc""",
					[uid])
	#trans_set = cursor.fetchall()
	#trans_set = CustomerTransactions.objects.all()
	table = transTable(trans_set)
	table.paginate(page=request.GET.get('page', 1), per_page=5)
	if len(list(trans_set)) == 0:
		tbl_msg = 'You have not performed any transactions till now.'

	buysell_form = buysellForm()
	compsearch_form = compsearchForm()
	sectorsearch_form = sectorsearchForm()

	msg_buysell = ''
	admin_uid = 1022
	bool_proceed = False
	if request.method == 'POST':
		if 'buy' in request.POST or 'sell' in request.POST:
			buysell_form = buysellForm(request.POST)
			if buysell_form.is_valid():
				stock_code=buysell_form.cleaned_data["stock_name"]			
				num_of_shares=buysell_form.cleaned_data["no_of_shares"]
			
				cursor.execute('SELECT current_price * %s AS total_cost, share_id FROM Shares_Details WHERE share_code = %s', 
											(num_of_shares, stock_code))			
				temp = cursor.fetchone()
				if temp == None:	
					msg_buysell = 'Invalid Stock Name. Please check the stock name and try again.'	
				else:		
					total_cost = temp[0]
					share_id = temp[1]

					cursor.execute('''SELECT (NVL(ud.user_brokerage_pct, ur.brokerage_pct) * %s)/100 brokerage_amount,										  
											  ca.current_bal
										FROM user_roles ur,
  											 customer_accounts ca,
  											 users_details ud
								   		WHERE ur.role_id       = ud.role_id
									 	AND ca.user_id         = ud.user_id									 
									 	AND ca.user_id         = %s
 									''',
 									(total_cost, uid))
					temp1=cursor.fetchone()
					brokerage_amount = temp1[0]				
					current_balance = temp1[1]
					
					if 'buy' in request.POST:
						if current_balance >= (total_cost+brokerage_amount):
							trans_type = 'BUY'
							trans_amount = total_cost + brokerage_amount
							bool_proceed = True
						else:						
							msg_buysell = 'Insufficient funds for Buying. Please try again'
					elif 'sell' in request.POST:
						cursor.execute('''SELECT ct.user_id, ct.share_id
										FROM customer_transactions ct
									   WHERE ct.user_id         = %s
										 AND ct.share_id        = %s
									GROUP BY ct.user_id, ct.share_id
								  	HAVING SUM(ct.no_of_shares) >= %s
 									''',
 									(uid, share_id, num_of_shares))
						temp = cursor.fetchone()
						if temp == None:
							msg_buysell = 'Not enough shares to sell for mentioned stock. Please try again.'
						else:
							trans_type = 'SELL'
							trans_amount = total_cost - brokerage_amount
							bool_proceed = True
					if bool_proceed:
						msg_buysell = '1'
						cursor.execute("""INSERT INTO customer_transactions 
												 VALUES (trans_id_seq.NEXTVAL, SYSDATE, (SELECT account_id 
												 										   FROM customer_accounts 
												 										  WHERE user_id =%s), 
														%s, %s, %s, %s, %s)""", 
										(uid, 
										uid, 
										share_id,
										num_of_shares,
										trans_amount,
										trans_type))

						cursor.execute("""INSERT INTO customer_transactions 
												 VALUES (trans_id_seq.NEXTVAL, SYSDATE, (SELECT account_id 
												 										   FROM customer_accounts 
												 										  WHERE user_id =%s), 
														%s, %s, %s, %s, 'BROKERAGE')""", 
										(admin_uid, 
										admin_uid, 			
										share_id,						
										num_of_shares,									
										brokerage_amount))
					

						if trans_type == 'BUY':
							trans_amount = -1*trans_amount				

						cursor.execute("""UPDATE customer_accounts SET current_bal = current_bal + %s
											WHERE user_id = %s""", (trans_amount, uid))
					

						cursor.execute("""UPDATE Customer_Accounts
											 SET current_bal = current_bal + %s
										   WHERE user_id = %s""", 
										(brokerage_amount, admin_uid))
					
						msg_buysell = 'Transaction Successfully Completed.'
						cursor.execute("commit")
					
						#HttpResponseRedirect('/blog/home/%s' %(user.get_username()))
		elif 'compsearch' in request.POST:
			compsearch_form = compsearchForm(request.POST)
			company_name = request.POST.get("company_name")						
			request.session['company_name'] = company_name
			'''if compsearch_form.is_valid():
				company_name = compsearch_form.cleaned_data["company_name"]
				
				msg_buysell = '2',company_name'''
			return redirect('/finapp/company/')
			#msg_buysell = '', company_name
		elif 'sectorsearch' in request.POST:
			sectorsearch_form = sectorsearchForm(request.POST)
			'''sector_name = request.POST.get("sector_name")						
			request.session['sector_name'] = sector_name'''
			if sectorsearch_form.is_valid():
				sector_id = sectorsearch_form.cleaned_data["sector_id"]
				request.session['sector_id'] = sector_id
				#msg_buysell = '1',sector_id
				return redirect('/finapp/sector/')
				
	cursor.close()				
	
	return render(request, 'finapp/home.html', {'full_name' : full_name,
												'role_name' : role_name,
												'last_login_time' : last_login_time,
												'total_loggedin_time' : total_loggedin_time, 
												'table' : table, 'tbl_msg' : tbl_msg,
												'buysell_form' : buysell_form,
												'compsearch_form' : compsearch_form,
												'sectorsearch_form' : sectorsearch_form,
												'msg_buysell' : msg_buysell})

def logout(request):
	a=1
	uid = request.session.get('uid')	
	cursor = connection.cursor()
	cursor.execute("""UPDATE Users_Details
						SET last_login_time = current_login_time,							
							last_logout_time = SYSDATE,
							total_loggedin_mins = NVL(total_loggedin_mins,0) + 60*24*(SYSDATE - current_login_time)							
							WHERE user_id = %s AND 1=%s""",
					(uid, a))
	cursor.execute("""UPDATE Users_Details
						SET current_login_time = NULL
							WHERE user_id = %s AND 1=%s""",
					(uid, a))
	cursor.execute("commit")	
	cursor.close()
	request.session.clear()
	return redirect('/finapp/')

def company(request):	
	company_name = request.session.get('company_name')	
	a = 1
	uid = request.session.get('uid')	
	cursor = connection.cursor()
	cursor.execute("""SELECT first_name||' '||last_name AS full_name, (SELECT role_name 
																		FROM user_roles 
																		WHERE role_id = ud.role_id) role_name
												FROM Users_Details ud WHERE user_id = %s AND 1=%s""",
					(uid,
					a))
	usr = cursor.fetchone()
	full_name = usr[0]	
	role_name = usr[1]
	cursor.close()
	profile_dtls = CompanyDetails.objects.raw("""SELECT company_id, CEO_NAME,
														(SELECT seg_name
															FROM segment_details
															WHERE seg_id = cd.segment_id) sector_name,
  														segment_id sector_id, web_url, address
													FROM company_details cd
													WHERE COMP_NAME = %s""", [company_name])[0]
	fin_dtls = CompanyFinance.objects.raw("""SELECT fin_id,
  													market_cap,
  													pe_ratio,
  													revenue,
  													profit_margin,
  													operating_margin,
  													FISCAL_YR_END_DATE
													FROM company_finance
													WHERE COMPANY_ID = %s""", [profile_dtls.company_id])[0]
	request.session['sector_id'] = profile_dtls.sector_id
	return render(request, 'finapp/company.html', {'company_name' : company_name,
													'profile_dtls' : profile_dtls,
													'full_name' : full_name,
													'role_name' : role_name,
													'fin_dtls' : fin_dtls})

def sector(request):
	sector_id = request.session.get('sector_id')
	tbl_msg = ''
	a = 1
	uid = request.session.get('uid')
	cursor = connection.cursor()
	cursor.execute("""SELECT first_name||' '||last_name AS full_name, (SELECT role_name 
																		FROM user_roles 
																		WHERE role_id = ud.role_id) role_name
												FROM Users_Details ud WHERE user_id = %s AND 1=%s""",
					(uid,
					a))
	usr = cursor.fetchone()
	full_name = usr[0]	
	role_name = usr[1]
	cursor.close()
	sector_dtls = SegmentDetails.objects.raw("""SELECT seg_id, seg_name,
														net_market_cap, 
														net_prof_margin,
														pe_ratio
													FROM segment_details
													WHERE seg_id = %s""", [sector_id])[0]
	
	segcomt_set = SharesDetails.objects.raw("""SELECT sd.share_id,
													cd.comp_name,
  													sd.share_code,
  													sd.current_price,
  													ROUND(100*(sd.current_price - sh.close_value)/sh.close_value, 2) change_pct
  												FROM company_details cd,
  													shares_details sd,
  													shares_history sh,
  													segment_details segd
  												WHERE cd.company_id = sd.company_id
  												AND sd.share_id        = sh.share_id
  												AND segd.seg_id        = cd.segment_id
  												AND sh.date_traded     =
  													(SELECT MAX(sh2.date_traded)
  														FROM shares_history sh2
  														WHERE sh2.share_id = sd.share_id 
  														AND sh2.date_traded <>
  															(SELECT MAX(sh3.date_traded) 
  																FROM shares_history sh3
  																WHERE sh2.share_id = sd.share_id)
  													  )
												AND segd.seg_id = %s""",[sector_dtls.seg_id])
	table = segcompTable(segcomt_set)
	table.paginate(page=request.GET.get('page', 1), per_page=5)
	if len(list(segcomt_set)) == 0:
		tbl_msg = 'There are no companies for this sector.'
	return render(request, 'finapp/sector.html', {'sector_dtls' : sector_dtls,
													'full_name' : full_name,
													'role_name'	: role_name,
													'tbl_msg' : tbl_msg,
													'table' : table})

def accounts(request):
	uid = request.session.get('uid')
	acct_msg = ''
	a = 1		
	acct_form = acctForm()
	cursor = connection.cursor()
	cursor.execute("""SELECT first_name||' '||last_name AS full_name, (SELECT role_name 
																		FROM user_roles 
																		WHERE role_id = ud.role_id) role_name
												FROM Users_Details ud WHERE user_id = %s AND 1=%s""",
					(uid,
					a))
	usr = cursor.fetchone()
	full_name = usr[0]	
	role_name = usr[1]	

	acct_dtls = CustomerAccounts.objects.raw("""SELECT account_id,
  													INITIAL_BAL,
  													ROUND(current_bal, 2) current_bal,
  													ROUND((current_bal - initial_bal), 2) prof_loss,
  													ROUND(100*(current_bal - initial_bal)/initial_bal, 2) prof_loss_pct
  												FROM customer_accounts
  												WHERE user_id = %s""",[uid])[0]
	if request.method == 'POST':
		acct_form = acctForm(request.POST)
		if acct_form.is_valid():
			topup_amount = acct_form.cleaned_data["topup_amount"]
			if acct_dtls.current_bal + topup_amount > 100000 :
				acct_msg = 'Current account balance cannot excceed $100,000'
			else:
				cursor = connection.cursor()
				cursor.execute("""UPDATE Customer_Accounts
									SET initial_bal = initial_bal + %s,
										current_bal = current_bal + %s
									WHERE account_id = %s""", 
								(topup_amount, topup_amount, acct_dtls.account_id))
				cursor.execute("commit")				
				acct_msg = 'Your account has been successfully credited. Refresh the page to see current account info.'
	cursor.close()
	return render(request, 'finapp/accounts.html', {'acct_msg' : acct_msg,
													'full_name' : full_name,
													'role_name' : role_name,
													'acct_dtls' : acct_dtls,
													'acct_form' : acct_form})

def shares(request):
	company_name = request.session.get('company_name')	
	shares_msg = ''
	a = 1
	uid = request.session.get('uid')
	cursor = connection.cursor()
	cursor.execute("""SELECT first_name||' '||last_name AS full_name, (SELECT role_name 
																		FROM user_roles 
																		WHERE role_id = ud.role_id) role_name
												FROM Users_Details ud WHERE user_id = %s AND 1=%s""",
					(uid,
					a))
	usr = cursor.fetchone()
	full_name = usr[0]	
	role_name = usr[1]
	cursor.close()
	tbl_msg = 'Click Search above.'
	form = histForm()
	empty_set = SharesHistory.objects.raw("SELECT * FROM shares_history WHERE 1=2")
	table = histTable(empty_set)	
	shares_dtls = SharesDetails.objects.raw("""SELECT sd.share_id,
  														sd.share_code, sd.date_traded_from,
  														round(100*(sd.current_price - sh.close_value)/sh.close_value, 2) pct_change,
  														close_value previous_close, sd.current_price
														FROM shares_details sd,
														shares_history sh,
														company_details cd
												WHERE sd.share_id   = sh.share_id
												AND cd.comp_name = %s
												AND sh.date_traded  =
													  (SELECT MAX(sh2.date_traded)
													    FROM shares_history sh2
													    WHERE sh2.share_id  = sd.share_id
													      AND sh2.date_traded <
													          (SELECT MAX(sh3.date_traded)
													              FROM shares_history sh3
													              WHERE sh3.share_id = sd.share_id
													           )
											)""", [company_name])[0]

	additional_info = SharesHistory.objects.raw("""SELECT sh1.*,
  														(SELECT MAX(sh3.h_day_high)
  															FROM shares_history sh3
  															WHERE sh3.share_id = sh1.share_id
  															AND sh3.date_traded BETWEEN (SYSDATE - 365) AND SYSDATE
  															AND sh3.h_day_high IS NOT NULL
  														) yearly_high,
  														(SELECT MIN(sh4.h_day_low)
  															FROM shares_history sh4
  															WHERE sh4.share_id = sh1.share_id
  															AND sh4.date_traded BETWEEN (SYSDATE - 365) AND SYSDATE
  														) yearly_low
													FROM shares_history sh1
													WHERE sh1.share_id  = %s
													AND sh1.date_traded =
  															(SELECT MAX(sh2.date_traded)
  																FROM shares_history sh2
  																WHERE sh2.share_id = sh1.share_id
  															)
												""", [shares_dtls.share_id])[0]
	if request.method == 'GET':
		form = histForm(request.GET)
		if form.is_valid():
			date_from = ifnull(form.cleaned_data["date_from"], datetime.strptime('01-01-1950', '%d-%m-%Y'))
			date_to = ifnull(form.cleaned_data["date_to"], datetime.now())
			value_from = ifnull(form.cleaned_data["value_from"], 0)
			value_to = ifnull(form.cleaned_data["value_to"], 100000)

			hist_tbl = SharesHistory.objects.raw("""SELECT *
													FROM shares_history
													WHERE share_id  = %s
													AND date_traded BETWEEN %s AND %s
													AND h_day_low > %s
													AND h_day_high < %s
													ORDER BY date_traded desc
												""", [shares_dtls.share_id, date_from, date_to, value_from, value_to])
			table = histTable(hist_tbl)
			table.paginate(page=request.GET.get('page', 1), per_page=25)
			if len(list(hist_tbl)) == 0:
				tbl_msg = 'There are no trading records in given range.'
			tbl_msg = ''
	return render(request, 'finapp/shares.html', {'shares_msg' : shares_msg,
													'shares_dtls' : shares_dtls,
													'additional_info' : additional_info,
													'form' : form,
													'full_name' : full_name,
													'role_name' : role_name,
													'table' : table,
													'tbl_msg' : tbl_msg})

def ifnull(var, val):
	if var is None:
		return val;
	return var;

def reports(request):
	a = 1
	uid = request.session.get('uid')
	cursor = connection.cursor()
	cursor.execute("""SELECT first_name||' '||last_name AS full_name, (SELECT role_name 
																		FROM user_roles 
																		WHERE role_id = ud.role_id) role_name
												FROM Users_Details ud WHERE user_id = %s AND 1=%s""",
					(uid,
					a))
	usr = cursor.fetchone()
	full_name = usr[0]	
	role_name = usr[1]
	cursor.close()
	form = reportsearchForm()
	rep_form = repselectForm()
	res_dtls = SharesHistory.objects.raw("""SELECT hist_id, '' pivot_point, '' support1, '' support2, 
													'' support3, '' resistance1, '' resistance2, '' resistance3
												FROM shares_history
												WHERE 1=2""")
	empty_tbl_set = [{"sel" : ""}]
	table = emptyTable(empty_tbl_set)
	msg = ''
	tbl_msg = ''
	if request.method == 'POST':
		if 'repsearch' in request.POST:
			form = reportsearchForm(request.POST)			
			if form.is_valid():
				share_id = form.cleaned_data["share_id"]
				time_frame = form.cleaned_data["time_frame"]
				res_dtls = SharesHistory.objects.raw("""SELECT temp3.hist_id, ROUND(pivot_point,2) pivot_point,
																ROUND(pivot_point - (0.382*(high_val - low_val)), 2) support1,
       															ROUND(pivot_point - (0.618*(high_val - low_val)), 2) support2,
       															ROUND(pivot_point - (1*(high_val - low_val)), 2) support3,
       															ROUND(pivot_point + (0.382*(high_val - low_val)), 2) resistance1,
       															ROUND(pivot_point + (0.618*(high_val - low_val)), 2) resistance2,
       															ROUND(pivot_point + (1*(high_val - low_val)), 2) resistance3
															FROM
																(SELECT temp2.high_val, 
        																temp2.low_val, 
        																sh2.close_value, 
        																(temp2.high_val+temp2.low_val+sh2.close_value)/3 pivot_point,
        																sh2.hist_id
  																	FROM
      																	(SELECT MAX(NVL(h_day_high,0)) high_val,
              																	MIN(NVL(h_day_low,0)) low_val, 
              																	temp.last_traded_date, sh.share_id
        																	FROM shares_history sh,
            																	(SELECT MAX(sh1.date_traded) last_traded_date, 
                    																	sh1.share_id
              																		FROM shares_history sh1
        																			WHERE sh1.share_id = %s
        																			GROUP BY sh1.share_id
      																			) temp
  																			WHERE sh.share_id = temp.share_id
  																			AND sh.date_traded BETWEEN 
  																					(temp.last_traded_date - 
  																						DECODE(%s, 
  																								'D', 1, 
  																								'W', 7, 
  																								'M', 30, 
  																								'Y', 365)
																					) AND temp.last_traded_date
  																			GROUP BY temp.last_traded_date, sh.share_id
  																		) temp2,
  																		shares_history sh2
																	WHERE sh2.date_traded = temp2.last_traded_date
																	AND sh2.share_id = temp2.share_id) temp3""", 
															[share_id, time_frame])[0]
	elif request.method == 'GET':
		if'repselect' in request.GET:
			rep_form = repselectForm(request.GET)			
			if rep_form.is_valid():
				rep_id = rep_form.cleaned_data["rep_id"]
				time_frame = rep_form.cleaned_data["time_frame"]
				if rep_id == '1':
					res_tbl = SharesHistory.objects.raw("""SELECT cd.comp_name,
  																	sd.share_code,
  																	seg.seg_name,
  																	sd.current_price,
  																	ROUND(100*(sh3.close_value-sh2.open_value)/sh2.open_value, 2) growth_pct,
  																	sh3.hist_id
																	FROM company_details cd,
  																		shares_details sd,
  																		segment_details seg,
  																		shares_history sh2,
  																		shares_history sh3,
  																		(SELECT MIN(sh.date_traded) first_traded_date,
    																			temp.last_traded_date,
    																			sh.share_id
  																				FROM shares_history sh,
    																			(SELECT MAX(sh1.date_traded) last_traded_date,
      																					sh1.share_id
    																				FROM shares_history sh1
    																			GROUP BY sh1.share_id
    																			) temp
  																			WHERE sh.share_id  = temp.share_id
  																			AND sh.date_traded > 
  																					(temp.last_traded_date - 
  																						DECODE(%s, 
  																								'D', 1, 
  																								'W', 7, 
  																								'M', 30, 
  																								'Y', 365
  																								)
																					)
  																			GROUP BY temp.last_traded_date, sh.share_id
  																		) temp1
																	WHERE sh2.share_id  = temp1.share_id
																	AND sh2.share_id    = sh3.share_id
																	AND sh2.date_traded = temp1.first_traded_date
																	AND sh3.date_traded = temp1.last_traded_date
																	AND sh2.share_id    = sd.share_id
																	AND sd.company_id   = cd.company_id
																	AND cd.segment_id   = seg.seg_id
																	ORDER BY ROUND(100*(sh3.close_value-sh2.open_value)/sh2.open_value, 2) DESC""",
														[time_frame])
					table = resTable(res_tbl)
				elif rep_id == '2':
					res_tbl = SharesDetails.objects.raw("""SELECT cd.comp_name,
  																	sd.share_code,
  																	seg.seg_name,
  																	sd.current_price,
  																	SUM(sh2.volume_traded) total_volume,
  																	sd.share_id
																FROM company_details cd,
  																	shares_details sd,
  																	segment_details seg,
  																	shares_history sh2,
  																	(SELECT MIN(sh.date_traded) first_traded_date,
    																		temp.last_traded_date,
    																		sh.share_id
  																		FROM shares_history sh,
    																		(SELECT MAX(sh1.date_traded) last_traded_date,
      																				sh1.share_id
    																			FROM shares_history sh1
    																		GROUP BY sh1.share_id
  																  			) temp
  																		WHERE sh.share_id  = temp.share_id
  																		AND sh.date_traded > 
  																				(temp.last_traded_date - DECODE(%s, 
  																												'D', 1, 
  																												'W', 7, 
  																												'M', 30, 
  																												'Y', 365)
																				)
  																		GROUP BY temp.last_traded_date,
		    																	sh.share_id
  																	) temp1
															WHERE sh2.share_id = temp1.share_id
															AND sh2.date_traded BETWEEN temp1.first_traded_date AND temp1.last_traded_date
															AND sh2.share_id  = sd.share_id
															AND sd.company_id = cd.company_id
															AND cd.segment_id = seg.seg_id
															GROUP BY cd.comp_name,
  																	sd.share_code,
  																	seg.seg_name,
  																	sd.current_price,
  																	sd.share_id
															ORDER BY SUM(sh2.volume_traded) DESC""",
														[time_frame])
					table = res2Table(res_tbl)
				elif rep_id == '3':
					res_tbl = SegmentDetails.objects.raw("""SELECT seg.seg_name,
  																	ROUND(AVG(
  																		ROUND(
  																			100*(sh3.close_value-sh2.open_value)
  																			/sh2.open_value
  																			, 2)
																		), 2) change_pct,
  																	seg.seg_id
																	FROM company_details cd,
  																		shares_details sd,
  																		segment_details seg,
  																		shares_history sh2,
  																		shares_history sh3,
  																		(SELECT MIN(sh.date_traded) first_traded_date,
    																			temp.last_traded_date,
    																			sh.share_id
  																				FROM shares_history sh,
    																			(SELECT MAX(sh1.date_traded) last_traded_date,
      																					sh1.share_id
    																				FROM shares_history sh1
    																			GROUP BY sh1.share_id
    																			) temp
  																			WHERE sh.share_id  = temp.share_id
  																			AND sh.date_traded > 
  																					(temp.last_traded_date - 
  																						DECODE(%s, 
  																								'D', 1, 
  																								'W', 7, 
  																								'M', 30, 
  																								'Y', 365
  																								)
																					)
  																			GROUP BY temp.last_traded_date, sh.share_id
  																		) temp1
																	WHERE sh2.share_id  = temp1.share_id
																	AND sh2.share_id    = sh3.share_id
																	AND sh2.date_traded = temp1.first_traded_date
																	AND sh3.date_traded = temp1.last_traded_date
																	AND sh2.share_id    = sd.share_id
																	AND sd.company_id   = cd.company_id
																	AND cd.segment_id   = seg.seg_id
                                  									GROUP BY seg.seg_name, seg.seg_id
																	ORDER BY AVG(
																				ROUND(
																					100*(sh3.close_value-sh2.open_value)
																					/sh2.open_value, 2)
																					) DESC""",
														[time_frame])
					table = res3Table(res_tbl)
				table.paginate(page=request.GET.get('page', 1), per_page=5)
				if len(list(res_tbl)) == 0:
					tbl_msg = 'There are no records for given range.'
											
	return render(request, 'finapp/reports.html', {'form' : form,
													'full_name' : full_name,
													'role_name' : role_name,
													'msg' : msg,
													'res_dtls' : res_dtls,
													'rep_form' : rep_form,													
													'table' : table,
													'tbl_msg' : tbl_msg})

def adminrep(request):
	uid = request.session.get('uid')	
	a = 1		
	rep_tbl_msg = ''
	empty_tbl_set = [{"sel" : ""}]
	admin_rep_table = emptyTable(empty_tbl_set)
	adminrep_form = adminrepForm()
	cursor = connection.cursor()	
	cursor.execute("""SELECT first_name||' '||last_name AS full_name, (SELECT role_name 
																		FROM user_roles 
																		WHERE role_id = ud.role_id) role_name
												FROM Users_Details ud WHERE user_id = %s AND 1=%s""",
					(uid,
					a))
	usr = cursor.fetchone()
	full_name = usr[0]	
	role_name = usr[1]	

	if request.method == 'GET':		
		if 'adminrepselect' in request.GET:
			adminrep_form = adminrepForm(request.GET)
			if adminrep_form.is_valid():
				admin_rep_id = adminrep_form.cleaned_data["admin_rep_id"]
				if admin_rep_id == '1':
					admin_rep_tbl = UsersDetails.objects.raw("""SELECT ud.user_id, ud.username,
  																			ud.first_name
  																			||' '
  																			||ud.last_name full_name,
  																			NVL(ud.user_brokerage_pct, ur.brokerage_pct) brokerage_pct,
  																			ur.role_name,
  																			ud.gender,
  																			ud.age
																		FROM users_details ud,
  																			user_roles ur
																		WHERE ud.role_id = ur.role_id
																		AND ud.creation_date BETWEEN SYSDATE-1 AND SYSDATE""")
					admin_rep_table = adminrep1Table(admin_rep_tbl)					
					if len(list(admin_rep_tbl)) == 0:
						rep_tbl_msg = 'There are no users added in the past 24 hrs.'
				elif admin_rep_id == '2':
					admin_rep_tbl = UsersDetails.objects.raw("""SELECT user_id, username,
  																		first_name
  																		||' '
  																		||last_name full_name,
  																		(SELECT role_name
  																			FROM user_roles
  																			WHERE role_id = ud.role_id) role_name
																	FROM users_details ud
																	WHERE current_login_time IS NOT NULL
																	AND user_id <> %s""",[uid])
					admin_rep_table = adminrep2Table(admin_rep_tbl)					
					if len(list(admin_rep_tbl)) == 0:
						rep_tbl_msg = 'There are no users active currently.'
				elif admin_rep_id == '3':
					admin_rep_tbl = UsersDetails.objects.raw("""SELECT ud.user_id, ud.first_name
  																		||' '
  																		||ud.last_name full_name,
  																		ca.initial_bal total_credited_amount,
  																		ROUND(ca.current_bal, 2) current_balance,
  																		NVL(
  																			(SELECT COUNT(1)
  																			FROM customer_transactions ct
  																			WHERE ct.user_id = ud.user_id
  																			AND CT.TRANS_DATE BETWEEN SYSDATE - 7 AND SYSDATE
  																			), 0) total_number_of_transactions,
  																		NVL(
  																			(SELECT ROUND(SUM(ct2.amount), 2)
  																				FROM customer_transactions ct2
  																				WHERE ct2.user_id  = ud.user_id
  																				AND ct2.trans_type = 'BUY'
  																				AND CT2.TRANS_DATE BETWEEN SYSDATE - 7 AND SYSDATE
  																			), 0) total_buy,
  																		NVL(
  																			(SELECT ROUND(SUM(ct2.amount), 2)
  																				FROM customer_transactions ct2
  																				WHERE ct2.user_id  = ud.user_id
  																				AND ct2.trans_type = 'SELL'
  																				AND CT2.TRANS_DATE BETWEEN SYSDATE - 7 AND SYSDATE
  																			), 0) total_sell
																	FROM users_details ud,
  																		customer_accounts ca,
  																		user_roles ur
																	WHERE ud.user_id  = ca.user_id
																	AND ur.role_id    = ud.role_id
																	AND ur.role_name <> 'ADMIN';""")
					admin_rep_table = adminrep3Table(admin_rep_tbl)					
					if len(list(admin_rep_tbl)) == 0:
						rep_tbl_msg = 'There are no users with non admin priviledges for you to moniter.'
				elif admin_rep_id == '4':
					admin_rep_tbl = CompanyDetails.objects.raw("""SELECT cd.company_id, 
																		CD.COMP_NAME company_name,
  																		sd.share_code,
  																		SD.CURRENT_PRICE current_value,
  																		NVL(
  																			(SELECT SUM(ct1.no_of_shares) 
  																			FROM customer_transactions ct1
  																			WHERE CT1.TRANS_TYPE  = 'BUY'
  																			AND SD.SHARE_ID     = CT1.SHARE_ID
  																			AND CT1.TRANS_DATE BETWEEN SYSDATE - 7 AND SYSDATE
  																			),0) volume_of_buy_orders,
  																		NVL(
  																			(SELECT SUM(ct2.no_of_shares)
  																			FROM customer_transactions ct2
  																			WHERE ct2.trans_type  = 'SELL'
  																			AND sd.share_id     = ct2.share_id
  																			AND CT2.TRANS_DATE BETWEEN SYSDATE - 7 AND SYSDATE
  																			),0) volume_of_sell_orders
																	FROM company_details cd,
  																		shares_details sd
																	WHERE CD.COMPANY_ID = SD.COMPANY_ID""")
					admin_rep_table = adminrep4Table(admin_rep_tbl)									
					if len(list(admin_rep_tbl)) == 0:
						rep_tbl_msg = 'There are no companies with active transactions in the past week.'
				RequestConfig(request, paginate={"per_page": 5}).configure(admin_rep_table)					
	cursor.close()
	return render(request, 'finapp/adminrep.html', {'full_name' : full_name,
													'role_name' : role_name,
													'adminrep_form'	: adminrep_form,
													'rep_tbl_msg' : rep_tbl_msg,
													'admin_rep_table' : admin_rep_table})	
						
def brokerageupd(request):
	uid = request.session.get('uid')	
	a = 1
	bupd_msg = ''
	tbl_msg = ''
	tuple_cnt = ''
	brokerageupd_form = brokerageupdForm()
	tuplecount_form = tuplecountForm()
	cursor = connection.cursor()	
	cursor.execute("""SELECT first_name||' '||last_name AS full_name, (SELECT role_name 
																		FROM user_roles 
																		WHERE role_id = ud.role_id) role_name
												FROM Users_Details ud WHERE user_id = %s AND 1=%s""",
					(uid,
					a))
	usr = cursor.fetchone()
	full_name = usr[0]	
	role_name = usr[1]	

	hni_tbl = CustomerAccounts.objects.raw("""SELECT ca.account_id, ud.username,
  														ud.first_name||' '||ud.last_name full_name,
  														NVL(
  															(SELECT ROUND(SUM(ct.amount),2)
  														 		FROM customer_transactions ct
  														 		WHERE ct.user_id = ud.user_id
  															), 
														0) total_transaction_amount,
  														ca.initial_bal total_cash_credits,
  														ca.current_bal current_balance
													FROM users_details ud,
  														user_roles ur,
  														customer_accounts ca
													WHERE ur.role_name = 'CUSTOMER'
													AND ur.role_id     = ud.role_id													
													AND ca.user_id     = ud.user_id
													ORDER BY NVL(
  															(SELECT ROUND(SUM(ct.amount),2)
  														 		FROM customer_transactions ct
  														 		WHERE ct.user_id = ud.user_id
  															), 
															0) DESC""")
	hni_table = hniTable(hni_tbl)
	hni_table.paginate(page=request.GET.get('page', 1), per_page=5)
	if len(list(hni_tbl)) == 0:
		tbl_msg = 'There are no users in the system.'
	if request.method == 'POST':
		if 'brokerageupd' in request.POST:
			brokerageupd_form = brokerageupdForm(request.POST)
			if brokerageupd_form.is_valid():
				userid = brokerageupd_form.cleaned_data["userid"]
				brokerage_p = brokerageupd_form.cleaned_data["brokerage_p"]			
				cursor.execute("""UPDATE users_details
									SET user_brokerage_pct = %s
										WHERE user_id = %s""", 
									(brokerage_p, userid))
				cursor.execute("commit")				
				bupd_msg = 'Successfully Updated brokerage percentage.'		
		elif 'tuplecount' in request.POST:
					tuple_cnt = 0
					cursor.execute("""SELECT SUM(num_rows) total_tuples
										FROM all_tables
										WHERE owner = 'ABRAJ'
										AND table_name NOT LIKE 'DJANGO%'
										AND table_name NOT LIKE 'AUTH%'
										AND status = 'VALID'""")
					tuple_cnt = cursor.fetchone()[0]
					'''
					cursor.execute("""SELECT table_name--SUM(num_rows) total_tuples
										FROM all_tables
										WHERE owner = 'ABRAJ'
										AND table_name NOT LIKE 'DJANGO%'
										AND table_name NOT LIKE 'AUTH%'
										AND status = 'VALID'""")
					
					qry = "SELECT COUNT(1) FROM "
					
					table_name = cursor.fetchall()
					#cursor.execute(qry)
					#tuple_cnt = tuple_cnt + cursor.fetchone()[0]
					for x in table_name:
						qry += ''.join(x)
						tuple_cnt = qry
						#cursor.execute(qry)
						#tuple_cnt = tuple_cnt + cursor.fetchone()[0]										
					'''
					if tuple_cnt == 0:
						tuple_cnt = 'No tables for said user.'
					
	cursor.close()
	return render(request, 'finapp/brokerageupd.html', {'hni_table' : hni_table,
													'tbl_msg'	: tbl_msg,
													'full_name' : full_name,
													'role_name' : role_name,
													'brokerageupd_form' : brokerageupd_form,
													'bupd_msg'	: bupd_msg,													
													'tuple_cnt'	: tuple_cnt,
													'tuplecount_form' : tuplecount_form})