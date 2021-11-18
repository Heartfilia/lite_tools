# 下面的字符可能不够准确 但是基本不会错

# unicode:在win和linux都不能正常显示的字符
__u_range_list = [1564, 6158, 7355, 7356, 12288, 65279, 65529, 65530, 65531] + list(range(8192, 8208)) + list(range(8232, 8240)) + list(range(8287, 8293)) + list(range(8294, 8304)) + list(range(55296, 57344))

# Unicode:在win上是能显示的字符 但是在linux上显示不出来的
__U_range_list = [1757, 1807, 2043, 2274, 2229, 4760, 13055, 12549, 12550] + list(range(1536, 1542)) + list(range(6170, 6175)) 


# 这里是mysql关键字列表
msyql_keywords = [
    "ACCESSIBLE",
    "ACCOUNT",
    "ACTION",
    "ACTIVE",
    "ADD",
    "ADMIN",
    "AFTER",
    "AGAINST",
    "AGGREGATE",
    "ALGORITHM",
    "ALL",
    "ALTER",
    "ALWAYS",
    "ANALYSE",
    "ANALYZE",
    "AND",
    "ANY",
    "ARRAY",
    "AS",
    "ASC",
    "ASCII",
    "ASENSITIVE",
    "AT",
    "ATTRIBUTE",
    "AUTHENTICATION",
    "AUTOEXTEND_SIZE",
    "AUTO_INCREMENT",
    "AVG",
    "AVG_ROW_LENGTH",
    "BACKUP",
    "BEFORE",
    "BEGIN",
    "BETWEEN",
    "BIGINT",
    "BINARY",
    "BINLOG",
    "BIT",
    "BLOB",
    "BLOCK",
    "BOOL",
    "BOOLEAN",
    "BOTH",
    "BTREE",
    "BUCKETS",
    "BY",
    "BYTE",
    "CACHE",
    "CALL",
    "CASCADE",
    "CASCADED",
    "CASE",
    "CATALOG_NAME",
    "CHAIN",
    "CHALLENGE_RESPONSE",
    "CHANGE",
    "CHANGED",
    "CHANNEL",
    "CHAR",
    "CHARACTER",
    "CHARSET",
    "CHECK",
    "CHECKSUM",
    "CIPHER",
    "CLASS_ORIGIN",
    "CLIENT",
    "CLONE",
    "CLOSE",
    "COALESCE",
    "CODE",
    "COLLATE",
    "COLLATION",
    "COLUMN",
    "COLUMNS",
    "COLUMN_FORMAT",
    "COLUMN_NAME",
    "COMMENT",
    "COMMIT",
    "COMMITTED",
    "COMPACT",
    "COMPLETION",
    "COMPONENT",
    "COMPRESSED",
    "COMPRESSION",
    "CONCURRENT",
    "CONDITION",
    "CONNECTION",
    "CONSISTENT",
    "CONSTRAINT",
    "CONSTRAINT_CATALOG",
    "CONSTRAINT_NAME",
    "CONSTRAINT_SCHEMA",
    "CONTAINS",
    "CONTEXT",
    "CONTINUE",
    "CONVERT",
    "CPU",
    "CREATE",
    "CROSS",
    "CUBE",
    "CUME_DIST",
    "CURRENT",
    "CURRENT_DATE",
    "CURRENT_TIME",
    "CURRENT_TIMESTAMP",
    "CURRENT_USER",
    "CURSOR",
    "CURSOR_NAME",
    "DATA",
    "DATABASE",
    "DATABASES",
    "DATAFILE",
    "DATE",
    "DATETIME",
    "DAY",
    "DAY_HOUR",
    "DAY_MICROSECOND",
    "DAY_MINUTE",
    "DAY_SECOND",
    "DEALLOCATE",
    "DEC",
    "DECIMAL",
    "DECLARE",
    "DEFAULT",
    "DEFAULT_AUTH",
    "DEFINER",
    "DEFINITION",
    "DELAYED",
    "DELAY_KEY_WRITE",
    "DELETE",
    "DENSE_RANK",
    "DESC",
    "DESCRIBE",
    "DESCRIPTION",
    "DES_KEY_FILE",
    "DETERMINISTIC",
    "DIAGNOSTICS",
    "DIRECTORY",
    "DISABLE",
    "DISCARD",
    "DISK",
    "DISTINCT",
    "DISTINCTROW",
    "DIV",
    "DO",
    "DOUBLE",
    "DROP",
    "DUAL",
    "DUMPFILE",
    "DUPLICATE",
    "DYNAMIC",
    "EACH",
    "ELSE",
    "ELSEIF",
    "EMPTY",
    "ENABLE",
    "ENCLOSED",
    "ENCRYPTION",
    "END",
    "ENDS",
    "ENFORCED",
    "ENGINE",
    "ENGINES",
    "ENGINE_ATTRIBUTE",
    "ENUM",
    "ERROR",
    "ERRORS",
    "ESCAPE",
    "ESCAPED",
    "EVENT",
    "EVENTS",
    "EVERY",
    "EXCEPT",
    "EXCHANGE",
    "EXCLUDE",
    "EXECUTE",
    "EXISTS",
    "EXIT",
    "EXPANSION",
    "EXPIRE",
    "EXPLAIN",
    "EXPORT",
    "EXTENDED",
    "EXTENT_SIZE",
    "FACTOR",
    "FAILED_LOGIN_ATTEMPTS",
    "FALSE",
    "FAST",
    "FAULTS",
    "FETCH",
    "FIELDS",
    "FILE",
    "FILE_BLOCK_SIZE",
    "FILTER",
    "FINISH",
    "FIRST",
    "FIRST_VALUE",
    "FIXED",
    "FLOAT",
    "FLOAT4",
    "FLOAT8",
    "FLUSH",
    "FOLLOWING",
    "FOLLOWS",
    "FOR",
    "FORCE",
    "FOREIGN",
    "FORMAT",
    "FOUND",
    "FROM",
    "FULL",
    "FULLTEXT",
    "FUNCTION",
    "GENERAL",
    "GENERATED",
    "GEOMCOLLECTION",
    "GEOMETRY",
    "GEOMETRYCOLLECTION",
    "GET",
    "GET_FORMAT",
    "GET_MASTER_PUBLIC_KEY",
    "GET_SOURCE_PUBLIC_KEY",
    "GLOBAL",
    "GRANT",
    "GRANTS",
    "GROUP",
    "GROUPING",
    "GROUPS",
    "GROUP_REPLICATION",
    "GTID_ONLY",
    "HANDLER",
    "HASH",
    "HAVING",
    "HELP",
    "HIGH_PRIORITY",
    "HISTOGRAM",
    "HISTORY",
    "HOST",
    "HOSTS",
    "HOUR",
    "HOUR_MICROSECOND",
    "HOUR_MINUTE",
    "HOUR_SECOND",
    "IDENTIFIED",
    "IF",
    "IGNORE",
    "IGNORE_SERVER_IDS",
    "IMPORT",
    "IN",
    "INACTIVE",
    "INDEX",
    "INDEXES",
    "INFILE",
    "INITIAL",
    "INITIAL_SIZE",
    "INITIATE",
    "INNER",
    "INOUT",
    "INSENSITIVE",
    "INSERT",
    "INSERT_METHOD",
    "INSTALL",
    "INSTANCE",
    "INT",
    "INT1",
    "INT2",
    "INT3",
    "INT4",
    "INT8",
    "INTEGER",
    "INTERVAL",
    "INTO",
    "INVISIBLE",
    "INVOKER",
    "IO",
    "IO_AFTER_GTIDS",
    "IO_BEFORE_GTIDS",
    "IO_THREAD",
    "IPC",
    "IS",
    "ISOLATION",
    "ISSUER",
    "ITERATE",
    "JOIN",
    "JSON",
    "JSON_TABLE",
    "JSON_VALUE",
    "KEY",
    "KEYRING",
    "KEYS",
    "KEY_BLOCK_SIZE",
    "KILL",
    "LAG",
    "LANGUAGE",
    "LAST",
    "LAST_VALUE",
    "LATERAL",
    "LEAD",
    "LEADING",
    "LEAVE",
    "LEAVES",
    "LEFT",
    "LESS",
    "LEVEL",
    "LIKE",
    "LIMIT",
    "LINEAR",
    "LINES",
    "LINESTRING",
    "LIST",
    "LOAD",
    "LOCAL",
    "LOCALTIME",
    "LOCALTIMESTAMP",
    "LOCK",
    "LOCKED",
    "LOCKS",
    "LOGFILE",
    "LOGS",
    "LONG",
    "LONGBLOB",
    "LONGTEXT",
    "LOOP",
    "LOW_PRIORITY",
    "MASTER",
    "MASTER_AUTO_POSITION",
    "MASTER_BIND",
    "MASTER_COMPRESSION_ALGORITHMS",
    "MASTER_CONNECT_RETRY",
    "MASTER_DELAY",
    "MASTER_HEARTBEAT_PERIOD",
    "MASTER_HOST",
    "MASTER_LOG_FILE",
    "MASTER_LOG_POS",
    "MASTER_PASSWORD",
    "MASTER_PORT",
    "MASTER_PUBLIC_KEY_PATH",
    "MASTER_RETRY_COUNT",
    "MASTER_SERVER_ID",
    "MASTER_SSL",
    "MASTER_SSL_CA",
    "MASTER_SSL_CAPATH",
    "MASTER_SSL_CERT",
    "MASTER_SSL_CIPHER",
    "MASTER_SSL_CRL",
    "MASTER_SSL_CRLPATH",
    "MASTER_SSL_KEY",
    "MASTER_SSL_VERIFY_SERVER_CERT",
    "MASTER_TLS_CIPHERSUITES",
    "MASTER_TLS_VERSION",
    "MASTER_USER",
    "MASTER_ZSTD_COMPRESSION_LEVEL",
    "MATCH",
    "MAXVALUE",
    "MAX_CONNECTIONS_PER_HOUR",
    "MAX_QUERIES_PER_HOUR",
    "MAX_ROWS",
    "MAX_SIZE",
    "MAX_UPDATES_PER_HOUR",
    "MAX_USER_CONNECTIONS",
    "MEDIUM",
    "MEDIUMBLOB",
    "MEDIUMINT",
    "MEDIUMTEXT",
    "MEMBER",
    "MEMORY",
    "MERGE",
    "MESSAGE_TEXT",
    "MICROSECOND",
    "MIDDLEINT",
    "MIGRATE",
    "MINUTE",
    "MINUTE_MICROSECOND",
    "MINUTE_SECOND",
    "MIN_ROWS",
    "MOD",
    "MODE",
    "MODIFIES",
    "MODIFY",
    "MONTH",
    "MULTILINESTRING",
    "MULTIPOINT",
    "MULTIPOLYGON",
    "MUTEX",
    "MYSQL_ERRNO",
    "NAME",
    "NAMES",
    "NATIONAL",
    "NATURAL",
    "NCHAR",
    "NDB",
    "NDBCLUSTER",
    "NESTED",
    "NETWORK_NAMESPACE",
    "NEVER",
    "NEW",
    "NEXT",
    "NO",
    "NODEGROUP",
    "NONE",
    "NOT",
    "NOWAIT",
    "NO_WAIT",
    "NO_WRITE_TO_BINLOG",
    "NTH_VALUE",
    "NTILE",
    "NULL",
    "NULLS",
    "NUMBER",
    "NUMERIC",
    "NVARCHAR",
    "OF",
    "OFF",
    "OFFSET",
    "OJ",
    "OLD",
    "ON",
    "ONE",
    "ONLY",
    "OPEN",
    "OPTIMIZE",
    "OPTIMIZER_COSTS",
    "OPTION",
    "OPTIONAL",
    "OPTIONALLY",
    "OPTIONS",
    "OR",
    "ORDER",
    "ORDINALITY",
    "ORGANIZATION",
    "OTHERS",
    "OUT",
    "OUTER",
    "OUTFILE",
    "OVER",
    "OWNER",
    "PACK_KEYS",
    "PAGE",
    "PARSER",
    "PARTIAL",
    "PARTITION",
    "PARTITIONING",
    "PARTITIONS",
    "PASSWORD",
    "PASSWORD_LOCK_TIME",
    "PATH",
    "PERCENT_RANK",
    "PERSIST",
    "PERSIST_ONLY",
    "PHASE",
    "PLUGIN",
    "PLUGINS",
    "PLUGIN_DIR",
    "POINT",
    "POLYGON",
    "PORT",
    "PRECEDES",
    "PRECEDING",
    "PRECISION",
    "PREPARE",
    "PRESERVE",
    "PREV",
    "PRIMARY",
    "PRIVILEGES",
    "PRIVILEGE_CHECKS_USER",
    "PROCEDURE",
    "PROCESS",
    "PROCESSLIST",
    "PROFILE",
    "PROFILES",
    "PROXY",
    "PURGE",
    "QUARTER",
    "QUERY",
    "QUICK",
    "RANDOM",
    "RANGE",
    "RANK",
    "READ",
    "READS",
    "READ_ONLY",
    "READ_WRITE",
    "REAL",
    "REBUILD",
    "RECOVER",
    "RECURSIVE",
    "REDOFILE",
    "REDO_BUFFER_SIZE",
    "REDUNDANT",
    "REFERENCE",
    "REFERENCES",
    "REGEXP",
    "REGISTRATION",
    "RELAY",
    "RELAYLOG",
    "RELAY_LOG_FILE",
    "RELAY_LOG_POS",
    "RELAY_THREAD",
    "RELEASE",
    "RELOAD",
    "REMOTE",
    "REMOVE",
    "RENAME",
    "REORGANIZE",
    "REPAIR",
    "REPEAT",
    "REPEATABLE",
    "REPLACE",
    "REPLICA",
    "REPLICAS",
    "REPLICATE_DO_DB",
    "REPLICATE_DO_TABLE",
    "REPLICATE_IGNORE_DB",
    "REPLICATE_IGNORE_TABLE",
    "REPLICATE_REWRITE_DB",
    "REPLICATE_WILD_DO_TABLE",
    "REPLICATE_WILD_IGNORE_TABLE",
    "REPLICATION",
    "REQUIRE",
    "REQUIRE_ROW_FORMAT",
    "RESET",
    "RESIGNAL",
    "RESOURCE",
    "RESPECT",
    "RESTART",
    "RESTORE",
    "RESTRICT",
    "RESUME",
    "RETAIN",
    "RETURN",
    "RETURNED_SQLSTATE",
    "RETURNING",
    "RETURNS",
    "REUSE",
    "REVERSE",
    "REVOKE",
    "RIGHT",
    "RLIKE",
    "ROLE",
    "ROLLBACK",
    "ROLLUP",
    "ROTATE",
    "ROUTINE",
    "ROW",
    "ROWS",
    "ROW_COUNT",
    "ROW_FORMAT",
    "ROW_NUMBER",
    "RTREE",
    "SAVEPOINT",
    "SCHEDULE",
    "SCHEMA",
    "SCHEMAS",
    "SCHEMA_NAME",
    "SECOND",
    "SECONDARY",
    "SECONDARY_ENGINE",
    "SECONDARY_ENGINE_ATTRIBUTE",
    "SECONDARY_LOAD",
    "SECONDARY_UNLOAD",
    "SECOND_MICROSECOND",
    "SECURITY",
    "SELECT",
    "SENSITIVE",
    "SEPARATOR",
    "SERIAL",
    "SERIALIZABLE",
    "SERVER",
    "SESSION",
    "SET",
    "SHARE",
    "SHOW",
    "SHUTDOWN",
    "SIGNAL",
    "SIGNED",
    "SIMPLE",
    "SKIP",
    "SLAVE",
    "SLOW",
    "SMALLINT",
    "SNAPSHOT",
    "SOCKET",
    "SOME",
    "SONAME",
    "SOUNDS",
    "SOURCE",
    "SOURCE_AUTO_POSITION",
    "SOURCE_BIND",
    "SOURCE_COMPRESSION_ALGORITHMS",
    "SOURCE_CONNECT_RETRY",
    "SOURCE_DELAY",
    "SOURCE_HEARTBEAT_PERIOD",
    "SOURCE_HOST",
    "SOURCE_LOG_FILE",
    "SOURCE_LOG_POS",
    "SOURCE_PASSWORD",
    "SOURCE_PORT",
    "SOURCE_PUBLIC_KEY_PATH",
    "SOURCE_RETRY_COUNT",
    "SOURCE_SSL",
    "SOURCE_SSL_CA",
    "SOURCE_SSL_CAPATH",
    "SOURCE_SSL_CERT",
    "SOURCE_SSL_CIPHER",
    "SOURCE_SSL_CRL",
    "SOURCE_SSL_CRLPATH",
    "SOURCE_SSL_KEY",
    "SOURCE_SSL_VERIFY_SERVER_CERT",
    "SOURCE_TLS_CIPHERSUITES",
    "SOURCE_TLS_VERSION",
    "SOURCE_USER",
    "SOURCE_ZSTD_COMPRESSION_LEVEL",
    "SPATIAL",
    "SPECIFIC",
    "SQL",
    "SQLEXCEPTION",
    "SQLSTATE",
    "SQLWARNING",
    "SQL_AFTER_GTIDS",
    "SQL_AFTER_MTS_GAPS",
    "SQL_BEFORE_GTIDS",
    "SQL_BIG_RESULT",
    "SQL_BUFFER_RESULT",
    "SQL_CACHE",
    "SQL_CALC_FOUND_ROWS",
    "SQL_NO_CACHE",
    "SQL_SMALL_RESULT",
    "SQL_THREAD",
    "SQL_TSI_DAY",
    "SQL_TSI_HOUR",
    "SQL_TSI_MINUTE",
    "SQL_TSI_MONTH",
    "SQL_TSI_QUARTER",
    "SQL_TSI_SECOND",
    "SQL_TSI_WEEK",
    "SQL_TSI_YEAR",
    "SRID",
    "SSL",
    "STACKED",
    "START",
    "STARTING",
    "STARTS",
    "STATS_AUTO_RECALC",
    "STATS_PERSISTENT",
    "STATS_SAMPLE_PAGES",
    "STATUS",
    "STOP",
    "STORAGE",
    "STORED",
    "STRAIGHT_JOIN",
    "STREAM",
    "STRING",
    "SUBCLASS_ORIGIN",
    "SUBJECT",
    "SUBPARTITION",
    "SUBPARTITIONS",
    "SUPER",
    "SUSPEND",
    "SWAPS",
    "SWITCHES",
    "SYSTEM",
    "TABLE",
    "TABLES",
    "TABLESPACE",
    "TABLE_CHECKSUM",
    "TABLE_NAME",
    "TEMPORARY",
    "TEMPTABLE",
    "TERMINATED",
    "TEXT",
    "THAN",
    "THEN",
    "THREAD_PRIORITY",
    "TIES",
    "TIME",
    "TIMESTAMP",
    "TIMESTAMPADD",
    "TIMESTAMPDIFF",
    "TINYBLOB",
    "TINYINT",
    "TINYTEXT",
    "TLS",
    "TO",
    "TRAILING",
    "TRANSACTION",
    "TRIGGER",
    "TRIGGERS",
    "TRUE",
    "TRUNCATE",
    "TYPE",
    "TYPES",
    "UNBOUNDED",
    "UNCOMMITTED",
    "UNDEFINED",
    "UNDO",
    "UNDOFILE",
    "UNDO_BUFFER_SIZE",
    "UNICODE",
    "UNINSTALL",
    "UNION",
    "UNIQUE",
    "UNKNOWN",
    "UNLOCK",
    "UNREGISTER",
    "UNSIGNED",
    "UNTIL",
    "UPDATE",
    "UPGRADE",
    "USAGE",
    "USE",
    "USER",
    "USER_RESOURCES",
    "USE_FRM",
    "USING",
    "UTC_DATE",
    "UTC_TIME",
    "UTC_TIMESTAMP",
    "VALIDATION",
    "VALUE",
    "VALUES",
    "VARBINARY",
    "VARCHAR",
    "VARCHARACTER",
    "VARIABLES",
    "VARYING",
    "VCPU",
    "VIEW",
    "VIRTUAL",
    "VISIBLE",
    "WAIT",
    "WARNINGS",
    "WEEK",
    "WEIGHT_STRING",
    "WHEN",
    "WHERE",
    "WHILE",
    "WINDOW",
    "WITH",
    "WITHOUT",
    "WORK",
    "WRAPPER",
    "WRITE",
    "X509",
    "XA",
    "XID",
    "XML",
    "XOR",
    "YEAR",
    "YEAR_MONTH",
    "ZEROFILL",
    "ZONE",
    "ACTIVE",
    "ADMIN",
    "ARRAY",
    "ATTRIBUTE",
    "AUTHENTICATION",
    "BUCKETS",
    "CHALLENGE_RESPONSE",
    "CLONE",
    "COMPONENT",
    "CUME_DIST",
    "DEFINITION",
    "DENSE_RANK",
    "DESCRIPTION",
    "EMPTY",
    "ENFORCED",
    "ENGINE_ATTRIBUTE",
    "EXCEPT",
    "EXCLUDE",
    "FACTOR",
    "FAILED_LOGIN_ATTEMPTS",
    "FINISH",
    "FIRST_VALUE",
    "FOLLOWING",
    "GEOMCOLLECTION",
    "GET_MASTER_PUBLIC_KEY",
    "GET_SOURCE_PUBLIC_KEY",
    "GROUPING",
    "GROUPS",
    "GTID_ONLY",
    "HISTOGRAM",
    "HISTORY",
    "INACTIVE",
    "INITIAL",
    "INITIATE",
    "INVISIBLE",
    "JSON_TABLE",
    "JSON_VALUE",
    "KEYRING",
    "LAG",
    "LAST_VALUE",
    "LATERAL",
    "LEAD",
    "LOCKED",
    "MASTER_COMPRESSION_ALGORITHMS",
    "MASTER_PUBLIC_KEY_PATH",
    "MASTER_TLS_CIPHERSUITES",
    "MASTER_ZSTD_COMPRESSION_LEVEL",
    "MEMBER",
    "NESTED",
    "NETWORK_NAMESPACE",
    "NOWAIT",
    "NTH_VALUE",
    "NTILE",
    "NULLS",
    "OF",
    "OFF",
    "OJ",
    "OLD",
    "OPTIONAL",
    "ORDINALITY",
    "ORGANIZATION",
    "OTHERS",
    "OVER",
    "PASSWORD_LOCK_TIME",
    "PATH",
    "PERCENT_RANK",
    "PERSIST",
    "PERSIST_ONLY",
    "PRECEDING",
    "PRIVILEGE_CHECKS_USER",
    "PROCESS",
    "RANDOM",
    "RANK",
    "RECURSIVE",
    "REFERENCE",
    "REGISTRATION",
    "REPLICA",
    "REPLICAS",
    "REQUIRE_ROW_FORMAT",
    "RESOURCE",
    "RESPECT",
    "RESTART",
    "RETAIN",
    "RETURNING",
    "REUSE",
    "ROLE",
    "ROW_NUMBER",
    "SECONDARY",
    "SECONDARY_ENGINE",
    "SECONDARY_ENGINE_ATTRIBUTE",
    "SECONDARY_LOAD",
    "SECONDARY_UNLOAD",
    "SKIP",
    "SOURCE_AUTO_POSITION",
    "SOURCE_BIND",
    "SOURCE_COMPRESSION_ALGORITHMS",
    "SOURCE_CONNECT_RETRY",
    "SOURCE_DELAY",
    "SOURCE_HEARTBEAT_PERIOD",
    "SOURCE_HOST",
    "SOURCE_LOG_FILE",
    "SOURCE_LOG_POS",
    "SOURCE_PASSWORD",
    "SOURCE_PORT",
    "SOURCE_PUBLIC_KEY_PATH",
    "SOURCE_RETRY_COUNT",
    "SOURCE_SSL",
    "SOURCE_SSL_CA",
    "SOURCE_SSL_CAPATH",
    "SOURCE_SSL_CERT",
    "SOURCE_SSL_CIPHER",
    "SOURCE_SSL_CRL",
    "SOURCE_SSL_CRLPATH",
    "SOURCE_SSL_KEY",
    "SOURCE_SSL_VERIFY_SERVER_CERT",
    "SOURCE_TLS_CIPHERSUITES",
    "SOURCE_TLS_VERSION",
    "SOURCE_USER",
    "SOURCE_ZSTD_COMPRESSION_LEVEL",
    "SRID",
    "STREAM",
    "SYSTEM",
    "THREAD_PRIORITY",
    "TIES",
    "TLS",
    "UNBOUNDED",
    "UNREGISTER",
    "VCPU",
    "VISIBLE",
    "WINDOW",
    "ZONE",
    "ANALYSE",
    "DES_KEY_FILE",
    "MASTER_SERVER_ID",
    "PARSE_GCOL_EXPR",
    "REDOFILE",
    "SQL_CACHE"
]

"""
根据Unicode5.0整理如下：

1）标准CJK文字
http://www.unicode.org/Public/UNIDATA/Unihan.html

2）全角ASCII、全角中英文标点、半宽片假名、半宽平假名、半宽韩文字母：FF00-FFEF
http://www.unicode.org/charts/PDF/UFF00.pdf

3）CJK部首补充：2E80-2EFF
http://www.unicode.org/charts/PDF/U2E80.pdf

4）CJK标点符号：3000-303F
http://www.unicode.org/charts/PDF/U3000.pdf

5）CJK笔划：31C0-31EF
http://www.unicode.org/charts/PDF/U31C0.pdf

6）康熙部首：2F00-2FDF
http://www.unicode.org/charts/PDF/U2F00.pdf

7）汉字结构描述字符：2FF0-2FFF
http://www.unicode.org/charts/PDF/U2FF0.pdf

8）注音符号：3100-312F
http://www.unicode.org/charts/PDF/U3100.pdf

9）注音符号（闽南语、客家语扩展）：31A0-31BF
http://www.unicode.org/charts/PDF/U31A0.pdf

10）日文平假名：3040-309F
http://www.unicode.org/charts/PDF/U3040.pdf

11）日文片假名：30A0-30FF
http://www.unicode.org/charts/PDF/U30A0.pdf

12）日文片假名拼音扩展：31F0-31FF
http://www.unicode.org/charts/PDF/U31F0.pdf

13）韩文拼音：AC00-D7AF
http://www.unicode.org/charts/PDF/UAC00.pdf

14）韩文字母：1100-11FF
http://www.unicode.org/charts/PDF/U1100.pdf

15）韩文兼容字母：3130-318F
http://www.unicode.org/charts/PDF/U3130.pdf

16）太玄经符号：1D300-1D35F
http://www.unicode.org/charts/PDF/U1D300.pdf

17）易经六十四卦象：4DC0-4DFF
http://www.unicode.org/charts/PDF/U4DC0.pdf

18）彝文音节：A000-A48F
http://www.unicode.org/charts/PDF/UA000.pdf

19）彝文部首：A490-A4CF
http://www.unicode.org/charts/PDF/UA490.pdf

20）盲文符号：2800-28FF
http://www.unicode.org/charts/PDF/U2800.pdf

21）CJK字母及月份：3200-32FF
http://www.unicode.org/charts/PDF/U3200.pdf

22）CJK特殊符号（日期合并）：3300-33FF
http://www.unicode.org/charts/PDF/U3300.pdf

23）装饰符号（非CJK专用）：2700-27BF
http://www.unicode.org/charts/PDF/U2700.pdf

24）杂项符号（非CJK专用）：2600-26FF
http://www.unicode.org/charts/PDF/U2600.pdf

25）中文竖排标点：FE10-FE1F
http://www.unicode.org/charts/PDF/UFE10.pdf

26）CJK兼容符号（竖排变体、下划线、顿号）：FE30-FE4F
http://www.unicode.org/charts/PDF/UFE30.pdf
"""