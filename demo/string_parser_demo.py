from lite_tools import clean_string


need_clean_string = "ðåå ä½ å¥½,ä¸å¥½.åç¹ãä¸ä½äººãå§\tåå\nè¿æä»ä¹\uFFFFååå"
print(clean_string(need_clean_string))

"""
- æ¸çæ¨¡å¼ å¯ä»¥ç»åä½¿ç¨ -> - 
"x"ï¼\\xå¼å¤´çç¬¦å· - 
"u": \\uè½¬ä¹æ¥éçç¬¦å· è¿æç©ºç½å­ç¬¦ - 
"U": å¨winä¸æå­ç¬¦linuxä¸æ¯ç©ºçå­ç¬¦ - 
"p": è±ææ ç¹(å«ç©ºæ ¼) - 
"P": ä¸­ææ ç¹ - 
"e": emoji - 
"s": å¸¸ç¨ç¹æ®ç¬¦å· å¦'\\t' '\\n' ä¸åå«ç©ºæ ¼ - 
"f": å¨è§å­ç¬¦  -- 
"r": é¢çå­ç¬¦æ¾ç¤ºä¸º Öè¿æ ·ç -

>>> clean_string(need_clean_string)   # é»è®¤å°±æ¯æ¸ç xuf  ææå°±æ¯x:\\xå¼å¤´ u:\\uå¼å¤´ è¿æf:å¨è§å­ç¬¦ 
>>> ðåå ä½ å¥½,ä¸å¥½.åç¹ãä¸ä½äººãå§	åå
è¿æä»ä¹ï¿¿ååå
>>> clean_string(need_clean_string, "xufs")   # sæ¯æ¸çpythonçè½¬ä¹å­ç¬¦ ç®ååªæ¸ç\\a \\b \\000 \\n \\v \\t \\r \\f  # è¿éæ¯åxæéå  ä¸è¿xä¸æ¸çå¸¸ç¨çç¬¦å·å¦åé¢ \\n \\v \\t \\r \\f
>>> ðåå ä½ å¥½,ä¸å¥½.åç¹ãä¸ä½äººãå§ååè¿æä»ä¹ï¿¿ååå
>>> clean_string(need_clean_string, "e")
>>> åå ä½ å¥½,ä¸å¥½.åç¹ãä¸ä½äººãå§	åå
è¿æä»ä¹ï¿¿ååå
>>> clean_string(need_clean_string, "pP")
>>> ðååä½ å¥½ä¸å¥½åç¹ä¸ä½äººå§	åå
è¿æä»ä¹ï¿¿ååå
>>> clean_string(need_clean_string, "pP", ' ')   # ç¬¬ä¸ä¸ªåæ°æ¯å¿½ç¥çå­ç¬¦ å¯ä»¥å¡«åå¤ä¸ªçåä¸ªå­ç¬¦ 
>>> ðåå ä½ å¥½ä¸å¥½åç¹ä¸ä½äººå§	åå
è¿æä»ä¹ï¿¿ååå  
>>> clean_string(need_clean_string, "sp")
>>> ðååä½ å¥½ä¸å¥½åç¹ãä¸ä½äººãå§ååè¿æä»ä¹ï¿¿ååå
>>> clean_string(need_clean_string, "us")
>>> ðåå ä½ å¥½,ä¸å¥½.åç¹ãä¸ä½äººãå§ååè¿æä»ä¹ï¿¿ååå
"""

from lite_tools import color_string
from loguru import logger

# color_string ç¬¬ä¸ä¸ªåæ°æ¯ä¼ å¥çå­ç¬¦ä¸²
# ç¬¬äºä¸ªåæ° å¦ææ¯åç¬çå­æèæ°å­ å°±æ¯è£é¥°å­ä½çé¢è²
#           å¦ææ¯å­å¸ é£ä¹å°±æ ¹æ®å­å¸éé¢çåæ°æ¥èªå®ä¹é¢è²æèå¶å®å±æ§
# å­å¸åæ°ï¼
# ç´æ¥åå­å¸ä¼ å¯ä»¥  ç¨**{}ä¼ ä¹å¯ä»¥
# f : font       å°±æ¯å­ä½é¢è²   é¢è²å¯ä»¥åä¸­æ è±æ ç®å å¯¹åºçè¾åºé¢è²ç¼ç   ä¸æ¯æé¢è²çåå­è¿å¶è¿ç§ åªè½ç¨æç»çé»è®¤ç(è¦ä¸ç¶å·¥ç¨éå¤ªå¤§ è¿ä¸ªä¸è¥¿ä¹ä¸éè¦ æ²¡å¿è¦)
# b : background èæ¯é¢è²
# v : view       æ¾ç¤ºçæ¹å¼     å¯ä»¥
# l/lenght :     è¾åºå­ç¬¦ä¸²çé¿åº¦
# ä¸é¢æ¯è¯¦ç»çæä½ ä¸éè¦å»æè®° ç¨ideçæ¶å æçå°±ä¼æç¤ºä¸é¢çä¸è¥¿
"""
:param string: ä¼ å¥çå­ç¬¦ä¸²
:param args  : åæ°æ³¨è§£å¦ä¸é¢æç¤º  ä¼ å¥éå­å¸ç±»åçæ¶å åªæç¬¬ä¸ä¸ªåæ°èµ·ä½ç¨å¨å­ä½é¢è²ä¸é¢  -->ä¼ å¥å­å¸åä¸æä½
:param kwargs: è¿éä¼ å¥éè¦ç¨ **{}   
:param f     : å­ä½é¢è² -> (30, é»è²/black)(31, çº¢è²/r/red)(32, ç»¿è²/g/green)(33, é»è²/y/yellow)(34, èè²/b/blue)(35, ç´«è²/p/purple)(36, éèè²/c/cyan)(37, ç½è²/w/white)
                        -> (90, darkgrey)(91, lightred)(92, lightgreen)(93, lightyellow)(94, lightblue)(95, pink)(96, lightcyan)
:param b     : èæ¯é¢è² -> (40, é»è²/black)(41, çº¢è²/r/red)(42, ç»¿è²/g/green)(43, é»è²/y/yellow)(44, èè²/b/blue)(45, ç´«è²/p/purple)(46, éèè²/c/cyan)(47, ç½è²/w/white)
:param v     : æ¾ç¤ºæ¹å¼ -> (0, éç½®/reset)(1, å ç²/b/bold)(2, ç¦æ­¢/disable)(4, ä½¿ç¨ä¸åçº¿/u/underline)(5, éªç/f/flash)(7, åç¸/r/reverse)(8, ä¸å¯è§/i/invisible)(9, å é¤çº¿/s/strikethrough)
"""
print(f"{'hello':<20}", "aaaaa")
print(color_string("hellow", {"f": "çº¢", "b": "ç½", "v": "strikethrough", "lenght": 20}), "aaaaa")
print(color_string("a", {"f": "çº¢", "b": "ç½", "v": "strikethrough", "l": 20}), "aaaaa")
print(color_string("hellow", {"f": "y", "b": "g"}), "aaaaa")
print(color_string("hellow", **{"f": "b", "b": "r"}), "aaaaa")
logger.info(f'{color_string("hellow", "çº¢")} aaaaa')

"""
è¿éæ¯color_string æ°å¢å çæ¹æ¡ è¿éåªè½è£é¥°æå®çé¢è² --åªè½ä¿®æ¹å­ä½-- é¢è²è£é¥°æ¹æ¡å¦ä¸
<red>xxx</red>          -- çº¢è²
<yellow>xxx</yellow>    -- é»è²
<blue>xxx</blue>        -- èè²
<green>xxx</green>      -- ç»¿è²
<cyan>xxx</cyan>        -- éè²
<purple>xxx</purple>    -- ç´«è²
<pink>xxx</pink>        -- ç²ä¸
<black>xxx</black>      -- é»è²
<white>xxx</white>      -- ç½è²
"""
# ä½¿ç¨æ¡ä¾
print(color_string("<red>ä»å¤©</red>ï¼ææ°å¢äºä¸ä¸ª<yellow>é¢è²</yellow>æ¹æ¡ï¼è®©<blue>color string</blue>ä½¿ç¨æ´å <green>æ¹ä¾¿.</green>"))


# match_case  åmatch caseä¸æ ·ä½¿ç¨
from lite_tools import match_case
# ä¸é¢çåè½ç±»ä¼¼ if_else ä¹åå¶å®è¯­æ³çswitch case

@match_case
def default_function(arg):
    return f"è¿éæ¯ä¸»å¥å£ ä¹æ¯é»è®¤è¿åå¼:{arg}"


@default_function.register("æ³¨åç¨å")
def test1(arg):
    return f"è¿éæ¯æ³¨åå¥½äºçå½æ°111111:ä¼ å¥çå¼>>{arg}"


@default_function.register("æµè¯2")
@default_function.register("test2")
def test2(arg):
    return f"æ¯æå¤å±åµå¥æ³¨å:ä¼ å¥çå¼>>{arg}"


@default_function.register_all(["111", 222])
def test3(arg):
    return f"ä¹æ¯æåè¡¨ï¼åç»ï¼éåçæ³¨åæ¹å¼ä¸æ¬¡æ§æ³¨åå®æ¯:ä¼ å¥çå¼>>{arg}"


print(default_function("é½æ²¡æ"))  # è¿éæ¯ä¸»å¥å£ ä¹æ¯é»è®¤è¿åå¼:é½æ²¡æ
print(default_function("æµè¯2"))   # æ¯æå¤å±åµå¥æ³¨å:ä¼ å¥çå¼>>æµè¯2
print(default_function(222))       # ä¹æ¯æåè¡¨ï¼åç»ï¼éåçæ³¨åæ¹å¼ä¸æ¬¡æ§æ³¨åå®æ¯:ä¼ å¥çå¼>>222


# ä¸é¢æ¯ä¸äºsqlçè¯­æ³æ¼æ¥ ç®ååªå¼äºå¢å æ¹  æ¥æ²¡æå¼ å é¤ä¹åªå¼äºdelete
# å¯è½æäºç»èæ²¡æå¼å® ä½æ¯å°±è¿æ ·äº æå¾å¼ç®å
# ä¸é¢æ¶åå°whereæä½çé½å¯ä»¥ç¨å­ç¬¦ä¸²å¤ç whereç¨å­å¸åªè½æ¯ ç­å¼
from lite_tools import SqlString


sql_obj = SqlString("test")   # è¿éä¼ å¥è¡¨å
print(sql_obj.insert({"name": "å¼ ä¸", "age": 12, "comment": "bad"}))   # INSERT INTO test (`name`, 'age', `comment`) VALUES ('å¼ ä¸', 12, 'bad');
print(sql_obj.insert({"name": "å¼ ä¸", "age": 12}, ignore=True))   # INSERT IGNORE INTO test (`name`, 'age') VALUES ('å¼ ä¸', 12);
print(sql_obj.update({"age": 66}, {"name": "å¼ ä¸"}))     # UPDATE test SET age = 66 WHERE `name` = 'å¼ ä¸';
print(sql_obj.update({"comment": "good"}, ["age<15", "name LIKES %å¼ %"]))  # UPDATE test SET `comment` = 'good' WHERE age<15 AND name LIKES %å¼ %;
print(sql_obj.delete({"age": 12}))                       # DELETE FROM test WHERE age = 12;
print(sql_obj.delete(where="age<12 AND name IS NULL"))   # DELETE FROM test WHERE age<12 AND name IS NULL;