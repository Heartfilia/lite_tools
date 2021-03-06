# 下面是下标和上标对应的键值关系
# 参考网站  https://unicode-table.com/cn/sets/superscript-and-subscript-letters/

# 有一些字母没有对应的关系

# 常用上标字符
_sup_string_normal = {
    "^0": "⁰",
    "^1": "¹",
    "^2": "²",
    "^3": "³",
    "^4": "⁴",
    "^5": "⁵",
    "^6": "⁶",
    "^7": "⁷",
    "^8": "⁸",
    "^9": "⁹",
    "^+": "⁺",
    "^-": "⁻",
    "^=": "⁼",
    "^(": "⁽",
    "^)": "⁾",
    "^a": "ᵃ",
    "^b": "ᵇ",
    "^c": "ᶜ",
    "^d": "ᵈ",
    "^e": "ᵉ",
    "^f": "ᶠ",
    "^g": "ᵍ",
    "^h": "ʰ",
    "^i": "ⁱ",
    "^j": "ʲ",
    "^k": "ᵏ",
    "^l": "ˡ",
    "^m": "ᵐ",
    "^n": "ⁿ",
    "^o": "ᵒ",
    "^p": "ᵖ",
    "^r": "ʳ",
    "^s": "ˢ",
    "^t": "ᵗ",
    "^u": "ᵘ",
    "^v": "ᵛ",
    "^w": "ʷ",
    "^x": "ˣ",
    "^y": "ʸ",
    "^z": "ᙆ",
    "^A": "ᴬ",
    "^B": "ᴮ",
    "^C": "ᒼ",
    "^D": "ᴰ",
    "^E": "ᴱ",
    "^G": "ᴳ",
    "^H": "ᴴ",
    "^I": "ᴵ",
    "^J": "ᴶ",
    "^K": "ᴷ",
    "^L": "ᴸ",
    "^M": "ᴹ",
    "^N": "ᴺ",
    "^O": "ᴼ",
    "^P": "ᴾ",
    "^R": "ᴿ",
    "^S": "",
    "^T": "ᵀ",
    "^U": "ᵁ",
    "^V": "ᵛ",  # 用的小写的替代
    "^W": "ᵂ",
    "^X": "ˣ",
    "^Y": "ᵞ",
    "^Z": "ᙆ"
}

# 常用下标字符
_substring = {
    "_0": "₀",
    "_1": "₁",
    "_2": "₂",
    "_3": "₃",
    "_4": "₄",
    "_5": "₅",
    "_6": "₆",
    "_7": "₇",
    "_8": "₈",
    "_9": "₉",
    "_+": "₊",
    "_-": "₋",
    "_=": "₌",
    "_(": "₍",
    "_)": "₎",
    "_a": "ₐ",
    "_e": "ₑ",
    "_h": "ₕ",
    "_i": "ᵢ",
    "_j": "ⱼ",
    "_k": "ₖ",
    "_l": "ₗ",
    "_m": "ₘ",
    "_n": "ₙ",
    "_o": "ₒ",
    "_p": "ₚ",
    "_r": "ᵣ",
    "_s": "ₛ",
    "_t": "ₜ",
    "_u": "ᵤ",
    "_v": "ᵥ",
    "_x": "ₓ"
}

# 常用的数学记号
_normal_math = {
    "&times;": "×",
    "&divide;": "÷",
    "&plusmn;": "±",
    "&ne;": "≠",
    "&deg;": "°",
    "&fnof;": "ƒ",
    "&sum;": "∑",
    "&pertenk;": "‱",
    "&part;": "∂",
    "&exist;": "∃",
    "&isin;": "∈",
    "&notin;": "∉",
    "&ni;": "∋",
    "&notni;": "∌",
    "&empty;": "∅",
    "&radic;": "√",
    "&prop;": "∝",
    "&infin;": "∞",
    "&ang;": "∠",
    "&parallel;": "∥",
    "&npar;": "∦",
    "&and;": "∧",
    "&or;": "∨",
    "&cap;": "∩",
    "&cup;": "∪",
    "&int;": "∫",
    "&iint;": "∬",
    "&iiint;": "∭",
    "&conint;": "∮",
    "&cconint;": "∯",
    "&ccconint;": "∰",
    "&cwint;": "∱",
    "&cwconint;": "∲",
    "&awconint;": "∳",
}

# 其它数学符号
_other_math = {
    "&not;": "¬",
    "&forall;": "∀",
    "&comp;": "∁",
    "&nexist;": "∄",
    "&nabla;": "∇",
    "&prod;": "∏",
    "&coprod;": "∐",
    "&mnplus;": "∓",
    "&plusdo;": "∔",
    "&setminus;": "∖",
    "&lowast;": "∗",
    "&compfn;": "∘",
    "&angrt;": "∟",
    "&angmsd;": "∡",
    "&angsph;": "∢",
    "&mid;": "∣",
    "&nmid;": "∤",
    "&therefore;": "∴",
    "&because;": "∵",
    "&ratio;": "∶",
    "&colon;": "∷",
    "&minusd;": "∸",
    "&mddot;": "∺",
    "&homtht;": "∻",
    "&sim;": "∼",
    "&bsim;": "∽",
    "&ac;": "∾",
    "&acd;": "∿",
    "&wreath;": "≀",
    "&nsim;": "≁",
    "&esim;": "≂",
    "&sime;": "≃",
    "&nsime;": "≄",
    "&cong;": "≅",
    "&simne;": "≆",
    "&ncong;": "≇",
    "&asymp;": "≈",
    "&nap;": "≉",
    "&approxeq;": "≊",
    "&apid;": "≋",
    "&bcong;": "≌",
    "&asympeq;": "≍",
    "&bump;": "≎",
    "&bumpe;": "≏",
    "&esdot;": "≐",
    "&edot;": "≑",
    "&efDot;": "≒",
    "&erDot;": "≓",
    "&colone;": "≔",
    "&ecolon;": "≕",
    "&ecir;": "≖",
    "&cire;": "≗",
    "&wedgeq;": "≙",
    "&veeeq;": "≚",
    "&trie;": "≜",
    "&equest;": "≟",
    "&equiv;": "≡",
    "&nequiv;": "≢",
    "&le;": "≤",
    "&ge;": "≥",
    "&lee;": "≦",
    "&gee;": "≧",
    "&lne;": "≨",
    "&gne;": "≩",
    "&lt;": "≪",
    "&gt;": "≫",
    "&between;": "≬",
    "&NotCupCap;": "≭",
    "&nlt;": "≮",
    "&ngt;": "≯",
    "&nle;": "≰",
    "&nge;": "≱",
    "&lsim;": "≲",
    "&gsim;": "≳",
    "&nlsim;": "≴",
    "&ngsim;": "≵",
    "&lg;": "≶",
    "&gl;": "≷",
    "&ntlg;": "≸",
    "&ntgl;": "≹",
    "&pr;": "≺",
    "&sc;": "≻",
    "&prcue;": "≼",
    "&sccue;": "≽",
    "&prsim;": "≾",
    "&scsim;": "≿",
    "&npr;": "⊀",
    "&nsc;": "⊁",
    "&sub;": "⊂",
    "&sup;": "⊃",
    "&nsub;": "⊄",
    "&nsup;": "⊅",
    "&sube;": "⊆",
    "&supe;": "⊇",
    "&nsube;": "⊈",
    "&nsupe;": "⊉",
    "&subne;": "⊊",
    "&supne;": "⊋",
    "&cupdot;": "⊍",
    "&uplus;": "⊎",
    "&sqsub;": "⊏",
    "&sqsup;": "⊐",
    "&sqsube;": "⊑",
    "&sqsupe;": "⊒",
    "&sqcap;": "⊓",
    "&sqcup;": "⊔",
    "&xwedge;": "⋀",
    "&xvee;": "⋁",
    "&xcap;": "⋂",
    "&xcup;": "⋃",
    "&oplus;": "⊕",
    "&ominus;": "⊖",
    "&otimes;": "⊗",
    "&osol;": "⊘",
    "&odot;": "⊙",
    "&ocir;": "⊚",
    "&oast;": "⊛",
    "&odash;": "⊝",
    "&plusb;": "⊞",
    "&minusb;": "⊟",
    "&timesb;": "⊠",
    "&sdotb;": "⊡",
    "&vdash;": "⊢",
    "&dashv;": "⊣",
    "&top;": "⊤",
    "&perp;": "⊥",
    "&models;": "⊧",
    "&vdasht;": "⊨",
    "&vdashq;": "⊩",
    "&vvdash;": "⊪",
    "&vdashl;": "⊫",
    "&nvdash;": "⊬",
    "&nvdasht;": "⊭",
    "&nvdashq;": "⊮",
    "&nvdashl;": "⊯",
    "&prurel;": "⊰",
    "&vltri;": "⊲",
    "&vrtri;": "⊳",
    "&ltrie;": "⊴",
    "&rtrie;": "⊵",
    "&origof;": "⊶",
    "&imof;": "⊷",
    "&mumap;": "⊸",
    "&hercon;": "⊹",
    "&intcal;": "⊺",
    "&veebar;": "⊻",
    "&barvee;": "⊽",
    "&angrtvb;": "⊾",
    "&lrtri;": "⊿",
    "&diamond;": "⋄",
    "&sdot;": "⋅",
    "&star;": "⋆",
    "&divonx;": "⋇",
    "&bowtie;": "⋈",
    "&ltimes;": "⋉",
    "&rtimes;": "⋊",
    "&lthree;": "⋋",
    "&rthree;": "⋌",
    "&bsime;": "⋍",
    "&cuvee;": "⋎",
    "&cuwed;": "⋏",
    "&ssub;": "⋐",
    "&ssup;": "⋑",
    "&ccap;": "⋒",
    "&ccup;": "⋓",
    "&fork;": "⋔",
    "&epar;": "⋕",
    "&ltdot;": "⋖",
    "&gtdot;": "⋗",
    "&lll;": "⋘",
    "&ggg;": "⋙",
    "&leg;": "⋚",
    "&gel;": "⋛",
    "&cuepr;": "⋞",
    "&cuesc;": "⋟",
    "&nprcue;": "⋠",
    "&nsccue;": "⋡",
    "&nsqsube;": "⋢",
    "&nsqsupe;": "⋣",
    "&lnsim;": "⋦",
    "&gnsim;": "⋧",
    "&prnsim;": "⋨",
    "&scnsim;": "⋩",
    "&nltri;": "⋪",
    "&nrtri;": "⋫",
    "&nltrie;": "⋬",
    "&nrtrie;": "⋭",
    "&vellip;": "⋮",
    "&ctdot;": "⋯",
    "&utdot;": "⋰",
    "&dtdot;": "⋱",
    "&disin;": "⋲",
    "&isinsv;": "⋳",
    "&isins;": "⋴",
    "&isindot;": "⋵",
    "&notinvc;": "⋶",
    "&notinvb;": "⋷",
    "&isinE;": "⋹",
    "&nisd;": "⋺",
    "&xnis;": "⋻",
    "&nis;": "⋼",
    "&notnivc;": "⋽",
    "&notnivb;": "⋾",
    "&lceil;": "⌈",
    "&rceil;": "⌉",
    "&lfloor;": "⌊",
    "&rfloor;": "⌋",
    "&lang;": "〈",
    "&rang;": "〉",
}

# 不常用上标字符
_sup_string_not_often = {
    "^&Alpha;": "ᵅ",
    "^&Ae;": "ᵆ",
    "^&Schwa;": "ᵊ",
    "^&OpenE;": "ᵋ",
    "^&TurnedOpenE;": "ᵌ",
    "^&TurnedI;": "ᵎ",
    "^&Eng;": "ᵑ",
    "^&OpenO;": "ᵓ",
    "^&TopHalfO;": "ᵔ",
    "^&BottomHalfO;": "ᵕ",
    "^&SidewaysU;": "ᵙ",
    "^&TurnedM;": "ᵚ",
    "^&Ain;": "ᵜ",
    "^&Beta;": "ᵝ",
    "^&Gamma;": "ᵞ",
    "^&Delta;": "ᵟ",
    "^&Phi;": "ᵠ",
    "^&Chi;": "ᵡ",
}

SUB_SUP_WORDS_HASH = dict(
    **_sup_string_normal, **_sup_string_not_often,
    **_substring, **_normal_math, **_other_math
)
