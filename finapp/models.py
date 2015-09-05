# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Remove `managed = False` lines for those models you wish to give write DB access
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.
from __future__ import unicode_literals

from django.db import models

class AuthGroup(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(unique=True, max_length=160, blank=True)
    class Meta:
        managed = False
        db_table = 'auth_group'

class AuthGroupPermissions(models.Model):
    id = models.IntegerField(primary_key=True)
    group = models.ForeignKey(AuthGroup)
    permission = models.ForeignKey('AuthPermission')
    class Meta:
        managed = False
        db_table = 'auth_group_permissions'

class AuthPermission(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100, blank=True)
    content_type = models.ForeignKey('DjangoContentType')
    codename = models.CharField(max_length=200, blank=True)
    class Meta:
        managed = False
        db_table = 'auth_permission'

class AuthUser(models.Model):
    id = models.IntegerField(primary_key=True)
    password = models.CharField(max_length=256, blank=True)
    last_login = models.DateTimeField()
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=60, blank=True)
    first_name = models.CharField(max_length=60, blank=True)
    last_name = models.CharField(max_length=60, blank=True)
    email = models.CharField(max_length=150, blank=True)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()
    class Meta:
        managed = False
        db_table = 'auth_user'

class AuthUserGroups(models.Model):
    id = models.IntegerField(primary_key=True)
    user = models.ForeignKey(AuthUser)
    group = models.ForeignKey(AuthGroup)
    class Meta:
        managed = False
        db_table = 'auth_user_groups'

class AuthUserUserPermissions(models.Model):
    id = models.IntegerField(primary_key=True)
    user = models.ForeignKey(AuthUser)
    permission = models.ForeignKey(AuthPermission)
    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'

class CompanyDetails(models.Model):
    company_id = models.BigIntegerField(primary_key=True)
    segment = models.ForeignKey('SegmentDetails', blank=True, null=True)
    comp_name = models.CharField(max_length=200)
    ceo_name = models.CharField(max_length=200, blank=True)
    address = models.CharField(max_length=2400, blank=True)
    web_url = models.CharField(max_length=240, blank=True)
    class Meta:
        managed = False
        db_table = 'company_details'

class CompanyFinance(models.Model):
    fin_id = models.BigIntegerField(primary_key=True)
    company = models.ForeignKey(CompanyDetails, blank=True, null=True)
    market_cap = models.FloatField(blank=True, null=True)
    pe_ratio = models.FloatField(blank=True, null=True)
    fiscal_yr_end_date = models.DateField(blank=True, null=True)
    revenue = models.FloatField(blank=True, null=True)
    profit_margin = models.FloatField(blank=True, null=True)
    operating_margin = models.FloatField(blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'company_finance'

class CustomerAccounts(models.Model):
    account_id = models.BigIntegerField(primary_key=True)
    user = models.ForeignKey('UsersDetails', blank=True, null=True)
    initial_bal = models.FloatField(blank=True, null=True)
    current_bal = models.FloatField(blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'customer_accounts'

class CustomerTransactions(models.Model):
    trans_id = models.BigIntegerField(primary_key=True)
    trans_date = models.DateField(blank=True, null=True)
    cust_account = models.ForeignKey(CustomerAccounts, blank=True, null=True)
    user = models.ForeignKey('UsersDetails', blank=True, null=True)
    share = models.ForeignKey('SharesDetails', blank=True, null=True)
    no_of_shares = models.BigIntegerField()
    amount = models.FloatField(blank=True, null=True)
    trans_type = models.CharField(max_length=80)
    class Meta:
        managed = False
        db_table = 'customer_transactions'

class DjangoAdminLog(models.Model):
    id = models.IntegerField(primary_key=True)
    action_time = models.DateTimeField()
    user = models.ForeignKey(AuthUser)
    content_type = models.ForeignKey('DjangoContentType', blank=True, null=True)
    object_id = models.TextField(blank=True)
    object_repr = models.CharField(max_length=400, blank=True)
    action_flag = models.IntegerField()
    change_message = models.TextField(blank=True)
    class Meta:
        managed = False
        db_table = 'django_admin_log'

class DjangoContentType(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=200, blank=True)
    app_label = models.CharField(max_length=200, blank=True)
    model = models.CharField(max_length=200, blank=True)
    class Meta:
        managed = False
        db_table = 'django_content_type'

class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=80)
    session_data = models.TextField(blank=True)
    expire_date = models.DateTimeField()
    class Meta:
        managed = False
        db_table = 'django_session'

class SegmentDetails(models.Model):
    seg_id = models.BigIntegerField(primary_key=True)
    seg_name = models.CharField(max_length=240)
    net_market_cap = models.FloatField(blank=True, null=True)
    net_prof_margin = models.FloatField(blank=True, null=True)
    pe_ratio = models.FloatField(blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'segment_details'

class SharesDetails(models.Model):
    share_id = models.BigIntegerField(primary_key=True)
    company = models.ForeignKey(CompanyDetails, blank=True, null=True)
    share_code = models.CharField(max_length=15)
    date_traded_from = models.DateField(blank=True, null=True)
    day_high = models.FloatField(blank=True, null=True)
    day_low = models.FloatField(blank=True, null=True)
    current_price = models.FloatField(blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'shares_details'

class SharesHistory(models.Model):
    hist_id = models.BigIntegerField(primary_key=True)
    share = models.ForeignKey(SharesDetails, blank=True, null=True)
    date_traded = models.DateField()
    open_value = models.FloatField(blank=True, null=True)
    h_day_high = models.FloatField(blank=True, null=True)
    h_day_low = models.FloatField(blank=True, null=True)
    close_value = models.FloatField(blank=True, null=True)
    volume_traded = models.BigIntegerField(blank=True, null=True)
    adjusted_close = models.FloatField(blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'shares_history'

class SharesHistoryStg(models.Model):
    date_traded = models.DateField()
    open_value = models.FloatField(blank=True, null=True)
    h_day_high = models.FloatField(blank=True, null=True)
    h_day_low = models.FloatField(blank=True, null=True)
    close_value = models.FloatField(blank=True, null=True)
    volume_traded = models.BigIntegerField(blank=True, null=True)
    adjusted_close = models.FloatField(blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'shares_history_stg'

class UserRoles(models.Model):
    role_id = models.BigIntegerField(primary_key=True)
    role_name = models.CharField(max_length=100)
    brokerage_pct = models.FloatField(blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'user_roles'

class UsersDetails(models.Model):
    user_id = models.BigIntegerField(primary_key=True)
    role = models.ForeignKey(UserRoles, blank=True, null=True)
    username = models.CharField(max_length=240)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    gender = models.CharField(max_length=10, blank=True)
    age = models.FloatField(blank=True, null=True)
    creation_date = models.DateField(blank=True, null=True)
    last_login_time = models.DateField(blank=True, null=True)
    last_logout_time = models.DateField(blank=True, null=True)
    password = models.CharField(max_length=240)
    total_loggedin_mins = models.FloatField(blank=True, null=True)
    current_login_time = models.DateField(blank=True, null=True)
    user_brokerage_pct = models.FloatField(blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'users_details'

