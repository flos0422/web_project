CREATE TABLE user_list (idx INTEGER PRIMARY KEY AUTOINCREMENT, ID varchar(20), NICK varchar(20), PW varchar(20), Email varchar(30), num int);
CREATE TABLE board (idx INTEGER PRIMARY KEY AUTOINCREMENT, b_title varchar(20), b_writer varchar(20), b_main TEXT, b_time TEXT, b_ID varchar(20), b_file TEXT);
CREATE TABLE comments (idx INTEGER PRIMARY KEY AUTOINCREMENT, b_idx int, c_writer varchar(20), c_main TEXT, c_time TEXT, c_ID varchar(20));
