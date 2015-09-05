from django.forms import ModelForm, PasswordInput, ChoiceField
from django import forms

from finapp.models import UsersDetails, CustomerTransactions, CompanyDetails, SegmentDetails, SharesHistory, SharesDetails

import django_tables2 as tables

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, ButtonHolder, Submit


class loginForm(ModelForm):		
	class Meta:
		model = UsersDetails
		fields = ('username', 'password')
		widgets = {
		'password': PasswordInput(),
		}		

	def __init__(self, *args, **kwargs):
       		super(loginForm, self).__init__(*args, **kwargs)
        	self.fields['username'].required = True	
        	self.fields['password'].required = True
        	self.helper = FormHelper()
        	self.helper.layout = Layout(
            				Fieldset(
                				'Login Form:',
                				'username',
                				'password'
            						),
            				ButtonHolder(
                				Submit('submit', 'Sign In', css_class='button white')
            						)
            					)

 
class signupForm(ModelForm):
	GENDER_CHOICES = (
        			('M', 'Male'),
        			('F', 'Female'),
    			)    	
	gender =  forms.ChoiceField(widget=forms.Select(), choices=GENDER_CHOICES)
	confirm_password = forms.CharField(widget=PasswordInput())

	def __init__(self, *args, **kwargs):
        	super(signupForm, self).__init__(*args, **kwargs)
        	self.fields['username'].required = True
        	self.fields['first_name'].required = True        
        	self.fields['age'].required = True
        	self.fields['password'].required = True
        	self.helper = FormHelper()
        	self.helper.layout = Layout(
            				Fieldset(
                				'New User? Register here:',
                				'username',
                				'first_name',
                				'last_name',
                				'gender',
                				'age',
                				'password',
                				'confirm_password'
            						),
            				ButtonHolder(
                				Submit('submit', 'Sign Up', css_class='button white')
            						)
            					)
	class Meta:
		model = UsersDetails
		fields = ('username', 'first_name', 'last_name', 'age', 'password')
		widgets = {
		'password': PasswordInput(),
		}				

class buysellForm(forms.Form):
	stock_name = forms.CharField(max_length=15, required=True)
	no_of_shares = forms.IntegerField(label='Number of Shares', required=True, min_value=1, max_value=200)
	def __init__(self, *args, **kwargs):
        	super(buysellForm, self).__init__(*args, **kwargs)
        	self.fields['stock_name'].required = True
        	self.fields['no_of_shares'].required = True        
        	self.helper = FormHelper()
        	self.helper.layout = Layout(
            				Fieldset(
                				'Place Buy/Sell Order:',
                				'stock_name',
                				'no_of_shares'
            						),
            				ButtonHolder(
                				Submit('buy', 'Buy', css_class='button white'),
                				Submit('sell', 'Sell', css_class='button white')
            						)
            					)
	

class transTable(tables.Table):
	share_code = tables.Column(verbose_name= 'Share Code')
	no_of_shares = tables.Column(verbose_name= 'Number of Shares')
	trans_type = tables.Column(verbose_name= 'Transaction Type')
	amount = tables.Column(verbose_name= 'Transaction Amount')
	trans_date = tables.Column(verbose_name='Transaction Date')

	class Meta:
		model = CustomerTransactions
		fields = ('no_of_shares', 'trans_type', 'amount', 'trans_date')
		sequence = ('share_code', 'no_of_shares', 'trans_type', 'amount', 'trans_date')
		attrs = {"class": "paleblue"}

class compsearchForm(forms.Form):
	company_name = forms.ModelChoiceField(queryset= CompanyDetails.objects.values_list('comp_name', flat = True), empty_label=None)
	'''def __init__(self, *args, **kwargs):
        	super(compsearchForm, self).__init__(*args, **kwargs)
        	self.helper = FormHelper()
        	self.helper.layout = Layout(
            				Fieldset(
                				'Company Search:',
                				'company_name'
            						),
            				ButtonHolder(
                				Submit('compsearch', 'Search', css_class='button white')
            						)
            					)'''
	
class sectorsearchForm(forms.Form):
	#sector_name = forms.ModelChoiceField(queryset= SegmentDetails.objects.values_list('seg_name', flat = True), empty_label=None)	
	sector_id =  forms.ChoiceField(widget=forms.Select(), choices=[(a.seg_id, a.seg_name) for a in SegmentDetails.objects.all()], label='Sector Name:')
	'''def __init__(self, *args, **kwargs):
        	super(sectorsearchForm, self).__init__(*args, **kwargs)
        	self.helper = FormHelper()
        	self.helper.layout = Layout(
            				Fieldset(
                				'Sector Search:',
                				'sector_name'
            						),
            				ButtonHolder(
                				Submit('sectorsearch', 'Search', css_class='button white')
            						)
            					)'''

class segcompTable(tables.Table):
	comp_name = tables.Column(verbose_name= 'Company Name')
	share_code = tables.Column(verbose_name= 'Share Code')
	current_price = tables.Column(verbose_name= 'Current share price')
	change_pct = tables.Column(verbose_name= 'Percent change for today')

	class Meta:
		attrs = {"class": "paleblue"}

class acctForm(forms.Form):
	topup_amount = forms.IntegerField(label='Enter amount to be added:', required=True, min_value=1, max_value=10000)
	def __init__(self, *args, **kwargs):
        	super(acctForm, self).__init__(*args, **kwargs)
        	self.helper = FormHelper()
        	self.helper.layout = Layout(
            				Fieldset(
                				'Balance too low? Top up here:',
                				'topup_amount',                				
            						),
            				ButtonHolder(
                				Submit('acct_button', 'Top Up!', css_class='button white')                				
            						)
            					)
	
class histForm(forms.Form):
	date_from = forms.DateField(label='Date From(DD-MM-YYYY):', required=False, input_formats=('%d-%m-%Y','%Y-%m-%d'))
	date_to = forms.DateField(label='Date To(DD-MM-YYYY):', required=False, input_formats=('%d-%m-%Y','%Y-%m-%d'))
	value_from = forms.IntegerField(label='Value From:', required=False, min_value=0)
	value_to = forms.IntegerField(label='Value To:', required=False, min_value=0)

class histTable(tables.Table):
	date_traded = tables.Column(verbose_name= 'Date Traded')
	open_value = tables.Column(verbose_name= 'Open Value')
	h_day_high = tables.Column(verbose_name= 'High')
	h_day_low = tables.Column(verbose_name= 'Low')
	close_value = tables.Column(verbose_name= 'Close Value')
	volume_traded = tables.Column(verbose_name= 'Volume')
	adjusted_close = tables.Column(verbose_name= 'Adjuested Close')

	class Meta:
		model = SharesHistory
		fields = ('date_traded', 'open_value', 'h_day_high', 'h_day_low', 'close_value', 'volume_traded', 'adjusted_close')
		attrs = {"class": "paleblue"}

class reportsearchForm(forms.Form):		
	share_id =  forms.ChoiceField(widget=forms.Select(), choices=[(a.share_id, a.share_code) for a in SharesDetails.objects.all()], label='Select a Stock Code!')
	TIME_CHOICES = (
        			('D', 'Tomorrow'),
        			('W', 'Next Week'),
        			('M', 'Next Month'),
        			('Y', 'Next Year'),
    			)    	
	time_frame =  forms.ChoiceField(widget=forms.Select(), choices=TIME_CHOICES, label='For time frame:')
	def __init__(self, *args, **kwargs):
        	super(reportsearchForm, self).__init__(*args, **kwargs)
        	self.helper = FormHelper()
        	self.helper.layout = Layout(
            				Fieldset(
                				'Check your Share Predictions:',
                				'share_id',
                				'time_frame'
            						),
            				ButtonHolder(
                				Submit('repsearch', 'Search', css_class='button white')
            						)
            					)

class repselectForm(forms.Form):		
	REP_CHOICES = (
					('1', 'Top performing Shares'),
					('2', 'Highest volumes'),
					('3', 'Top performing sectors')
				)
	rep_id =  forms.ChoiceField(widget=forms.RadioSelect(), choices=REP_CHOICES, label='Select the report you want to run!')
	
	TIME_CHOICES = (
        			('D', 'Last Day'),
        			('W', 'Last Week'),
        			('M', 'Last Month'),
        			('Y', 'Last Year'),
    			)    	
	time_frame =  forms.ChoiceField(widget=forms.Select(), choices=TIME_CHOICES, label='For time frame:')
	
	def __init__(self, *args, **kwargs):
        	super(repselectForm, self).__init__(*args, **kwargs)
        	self.helper = FormHelper()
        	self.helper.layout = Layout(
            				Fieldset(
                				'Run a Report:',
                				'rep_id',
                				'time_frame'
            						),
            				ButtonHolder(
                				Submit('repselect', 'Run', css_class='button white')
            						)
            					)        	

class resTable(tables.Table):
	comp_name = tables.Column(verbose_name= 'Company Name')
	share_code = tables.Column(verbose_name= 'Share Code')
	seg_name = tables.Column(verbose_name= 'Sector')
	current_price = tables.Column(verbose_name= 'Current Share Price')
	growth_pct = tables.Column(verbose_name= 'Percentage Change')

	class Meta:		
		attrs = {"class": "paleblue"}        	

class res2Table(tables.Table):
	comp_name = tables.Column(verbose_name= 'Company Name')
	share_code = tables.Column(verbose_name= 'Share Code')
	seg_name = tables.Column(verbose_name= 'Sector')
	current_price = tables.Column(verbose_name= 'Current Share Price')
	total_volume = tables.Column(verbose_name= 'Total Volume')

	class Meta:		
		attrs = {"class": "paleblue"}    

class res3Table(tables.Table):
	seg_name = tables.Column(verbose_name= 'Sector Name')
	change_pct = tables.Column(verbose_name= 'Cumulative change percentage')

	class Meta:		
		attrs = {"class": "paleblue"}    

class emptyTable(tables.Table):
	sel = tables.Column(verbose_name="Select report type.")		

class hniTable(tables.Table):
	username = tables.Column(verbose_name= 'Username')
	full_name = tables.Column(verbose_name= 'Full Name')
	total_transaction_amount = tables.Column(verbose_name= 'Total Transaction Amount($)')
	total_cash_credits = tables.Column(verbose_name= 'Total Cash Credits($)')
	current_balance = tables.Column(verbose_name= 'Current Balance($)')

	class Meta:		
		attrs = {"class": "paleblue"}

class brokerageupdForm(forms.Form):			
	userid =  forms.ChoiceField(widget=forms.Select(), choices=[(a.user_id, a.username) for a in UsersDetails.objects.all()], label='Select a User')
	
	brokerage_p = forms.IntegerField(label="Brokerage Percentage", required=True, min_value=0, max_value=3)
	
	def __init__(self, *args, **kwargs):
        	super(brokerageupdForm, self).__init__(*args, **kwargs)
        	self.helper = FormHelper()
        	self.helper.layout = Layout(
            				Fieldset(
                				'Update brokerage for a user:',
                				'userid',
                				'brokerage_p'
            						),
            				ButtonHolder(
                				Submit('brokerageupd', 'Update', css_class='button white')
            						)
            					)        			

class adminrepForm(forms.Form):		
	ADMIN_REP_CHOICES = (
					('1', 'Users registered within last 24 hours'),
					('2', 'Currently active users'),
					('3', 'Accounting details for all users'),
					('4', 'Transaction summary per company for last week')
				)
	admin_rep_id =  forms.ChoiceField(widget=forms.RadioSelect(), choices=ADMIN_REP_CHOICES, label='Select the report you want to run!')	
	
	def __init__(self, *args, **kwargs):
        	super(adminrepForm, self).__init__(*args, **kwargs)
        	self.helper = FormHelper()
        	self.helper.layout = Layout(
            				Fieldset(
                				'Run a Report:',
                				'admin_rep_id'                				
            						),
            				ButtonHolder(
                				Submit('adminrepselect', 'Run', css_class='button white')
            						)
            					)        	

class adminrep1Table(tables.Table):
	username = tables.Column(verbose_name= 'Username')
	full_name = tables.Column(verbose_name= 'Full Name')
	brokerage_pct = tables.Column(verbose_name= 'Brokerage Percentage')
	role_name = tables.Column(verbose_name= 'Role')
	gender = tables.Column(verbose_name= 'Gender')
	age = tables.Column(verbose_name= 'Age')

	class Meta:		
		attrs = {"class": "paleblue"}

class adminrep2Table(tables.Table):
	username = tables.Column(verbose_name= 'Username')
	full_name = tables.Column(verbose_name= 'Full Name')	
	role_name = tables.Column(verbose_name= 'Role')
	
	class Meta:		
		attrs = {"class": "paleblue"}

class adminrep3Table(tables.Table):	
	full_name = tables.Column(verbose_name= 'Full Name')	
	total_credited_amount = tables.Column(verbose_name= 'Total Credited Amount')
	current_balance = tables.Column(verbose_name= 'Current Balance')
	total_number_of_transactions = tables.Column(verbose_name= 'Total Number of Transactions')
	total_buy = tables.Column(verbose_name= 'Total Buy')
	total_sell = tables.Column(verbose_name= 'Total Sell')
	
	class Meta:		
		attrs = {"class": "paleblue"}

class adminrep4Table(tables.Table):	
	company_name = tables.Column(verbose_name= 'Company Name')	
	share_code = tables.Column(verbose_name= 'Stock Code')
	current_value = tables.Column(verbose_name= 'Current Value')
	volume_of_buy_orders = tables.Column(verbose_name= 'Volume of BUY Orders')
	volume_of_sell_orders = tables.Column(verbose_name= 'Volume of SELL Orders')	
	
	class Meta:		
		attrs = {"class": "paleblue"}

class tuplecountForm(forms.Form):			
	def __init__(self, *args, **kwargs):
        	super(tuplecountForm, self).__init__(*args, **kwargs)
        	self.helper = FormHelper()
        	self.helper.layout = Layout(
            				Fieldset(
                				'Tuple Count:'
                				),
            				ButtonHolder(
                				Submit('tuplecount', 'Tuple Count for DB', css_class='button white')
            						)
            					)        			