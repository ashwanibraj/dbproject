CREATE TABLE user_roles
(role_id    INT,
role_name   VARCHAR2(100) NOT NULL,
brokerage_pct NUMBER,
PRIMARY KEY (role_id)
);

DESC user_roles;

Role id 100 - Customer - 2%
Role id 200 - Admin - 0%

CREATE TABLE users_details
  (user_id    		INT,
  role_id     		INT,
  username    		VARCHAR2(240) NOT NULL,
  password		VARCHAR2(240) NOT NULL,
  first_name  		VARCHAR2(100) NOT NULL,
  last_name   		VARCHAR2(100) NOT NULL,
  gender      		VARCHAR2(1),
  age         		NUMBER,
  creation_date 	DATE,
  last_login_time  	DATE,
  last_logout_time 	DATE,
  PRIMARY KEY (user_id),
  FOREIGN KEY (role_id) REFERENCES user_roles(role_id)
  );

CREATE SEQUENCE user_id_seq
 START WITH     1000
 INCREMENT BY   1
 NOCACHE
 NOCYCLE;

CREATE TABLE customer_accounts
  (account_id INT,
  user_id         INT,
  initial_bal     NUMBER,
  current_bal     NUMBER,
  PRIMARY KEY (account_id),
  FOREIGN KEY (user_id) references users_details(user_id)
  );

host account - 11003

CREATE SEQUENCE account_id_seq
 START WITH     11000
 INCREMENT BY   1
 NOCACHE
 NOCYCLE;
  
CREATE TABLE  segment_details
  (seg_id          INT,
  seg_name        VARCHAR2(240) NOT NULL,
  composite_value NUMBER,
  net_market_cap  NUMBER,
  net_prof_margin NUMBER,
  PRIMARY KEY (seg_id)
  );

CREATE SEQUENCE segment_id_seq
 START WITH     144
 INCREMENT BY   1
 NOCACHE
 NOCYCLE;


CREATE TABLE company_details
  (company_id      INT,
  segment_id      INT,
  comp_name       VARCHAR2(200) NOT NULL,
  CEO_name        VARCHAR2(200),
  address         VARCHAR2(2400),
  web_url         VARCHAR2(240),
  PRIMARY KEY (company_id),
  FOREIGN KEY (segment_id) REFERENCES segment_details(seg_id)
  );

CREATE SEQUENCE company_id_seq
 START WITH     255
 INCREMENT BY   1
 NOCACHE
 NOCYCLE;


CREATE TABLE company_finance
  (fin_id  		INT,
  company_id      INT,
  market_cap      NUMBER,
  PE_ratio        NUMBER,
  fiscal_yr_end_date  DATE,
  revenue         NUMBER,
  profit_margin   NUMBER,
  operating_margin NUMBER,
  PRIMARY KEY (fin_id),
  FOREIGN KEY (company_id) REFERENCES company_details(company_id)
  );

CREATE SEQUENCE fin_id_seq
 START WITH     800
 INCREMENT BY   1
 NOCACHE
 NOCYCLE;
  
CREATE TABLE shares_details
  (share_id        INT,
  company_id       INT,
  share_code       VARCHAR2(15) NOT NULL,
  date_traded_from DATE,
  day_high         NUMBER,
  day_low          NUMBER,
  current_price    NUMBER,
  PRIMARY KEY (share_id),
  FOREIGN KEY (company_id) REFERENCES company_details(company_id)
  );

CREATE TABLE shares_history
  (hist_id        INT,
  share_id        INT,
  date_traded     DATE NOT NULL,
  open_value      NUMBER,
  h_day_high      NUMBER,
  h_day_low       NUMBER,
  close_value     NUMBER,
  volume_traded   INT,
  adjusted_close  NUMBER,
  PRIMARY KEY (hist_id),
  FOREIGN KEY (share_id) REFERENCES shares_details(share_id)
  );

CREATE SEQUENCE hist_id_seq
 START WITH     100000
 INCREMENT BY   1
 NOCACHE
 NOCYCLE;

CREATE TABLE customer_transactions
  (trans_id  	INT,
  trans_date       DATE,
  cust_account_id  INT,
  user_id          INT,
  share_id         INT,
  no_of_shares     INT NOT NULL,
  amount	       NUMBER,
  trans_type       VARCHAR2(80) NOT NULL,
  PRIMARY KEY (trans_id),
  FOREIGN KEY (cust_account_id) REFERENCES customer_accounts(account_id),
  FOREIGN KEY (user_id) REFERENCES users_details(user_id),
  FOREIGN KEY (share_id) REFERENCES shares_details(share_id)
  );

CREATE SEQUENCE trans_id_seq
 START WITH     51000
 INCREMENT BY   1
 NOCACHE
 NOCYCLE;
