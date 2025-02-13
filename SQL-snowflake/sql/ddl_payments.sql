create or replace TABLE PAYMENTS (
	PAYMENT_ID NUMBER(38,0) NOT NULL,
	ORDER_ID NUMBER(38,0),
	PAYMENT_DATE DATE,
	AMOUNT NUMBER(10,2),
	primary key (PAYMENT_ID),
	foreign key (ORDER_ID) references ORDER_DETAILS(ORDER_ID)
);
