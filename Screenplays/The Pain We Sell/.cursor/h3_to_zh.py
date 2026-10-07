#!/usr/bin/env python3
"""Rewrite MiniMax H3 paste blocks into Chinese and correct known story mismatches."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path("/Users/vimchain/Obsidian/Screenplays/The Pain We Sell/MiniMax H3.md")

MM = {
    "28": "二十八",
    "32": "三十二",
    "35": "三十五",
    "40": "四十",
    "45": "四十五",
    "50": "五十",
    "55": "五十五",
    "60": "六十",
    "65": "六十五",
    "70": "七十",
    "75": "七十五",
    "80": "八十",
    "85": "八十五",
    "90": "九十",
    "100": "一百",
    "120": "一百二十",
}


def protect(text: str) -> tuple[str, list[str]]:
    vault: list[str] = []

    def grab(m: re.Match) -> str:
        vault.append(m.group(0))
        return f"⟦{len(vault) - 1}⟧"

    text = re.sub(r"`[^`]*`|\"[^\"]*\"", grab, text)
    return text, vault


def restore(text: str, vault: list[str]) -> str:
    def put(m: re.Match) -> str:
        return vault[int(m.group(1))]

    return re.sub(r"⟦(\d+)⟧", put, text)


def cn_mm(n: str) -> str:
    return MM.get(n, n) + "毫米"


SHOT = [
    (r"Cinematic subjective tight close-up on the hands", "真人实拍手部大特写，主观"),
    (r"Cinematic tight close-up on the hands", "真人实拍手部大特写"),
    (r"Cinematic medium close-up on the hands", "真人实拍手部中近景"),
    (r"Cinematic close-up on the hands", "真人实拍手部近景"),
    (r"Cinematic medium shot on the hands", "真人实拍手部中景"),
    (r"Cinematic extreme close-up", "真人实拍大特写"),
    (r"Cinematic subjective tight close-up", "真人实拍主观大特写"),
    (r"Cinematic subjective looking-down shot", "真人实拍主观俯拍"),
    (r"Cinematic subjective medium close-up", "真人实拍主观中近景"),
    (r"Cinematic subjective medium-full shot", "真人实拍主观中全景"),
    (r"Cinematic subjective medium shot", "真人实拍主观中景"),
    (r"Cinematic subjective wide shot", "真人实拍主观全景"),
    (r"Cinematic subjective close-up", "真人实拍主观近景"),
    (r"Cinematic subjective two-shot", "真人实拍主观双人"),
    (r"Cinematic subjective shot", "真人实拍主观镜头"),
    (r"Cinematic over-shoulder medium close-up", "真人实拍过肩中近景"),
    (r"Cinematic over-shoulder close-up", "真人实拍过肩近景"),
    (r"Cinematic over-shoulder", "真人实拍过肩"),
    (r"Cinematic asymmetric two-shot", "真人实拍不对称双人"),
    (r"Cinematic medium close-up two-shot", "真人实拍双人中近景"),
    (r"Cinematic two-shot close-up", "真人实拍双人近景"),
    (r"Cinematic side medium two-shot", "真人实拍侧面双人中景"),
    (r"Cinematic side medium close-up", "真人实拍侧面中近景"),
    (r"Cinematic side two-shot", "真人实拍侧面双人"),
    (r"Cinematic medium two-shot", "真人实拍双人中景"),
    (r"Cinematic two-shot medium", "真人实拍双人中景"),
    (r"Cinematic wide two-shot", "真人实拍宽幅双人"),
    (r"Cinematic two-shot", "真人实拍双人镜头"),
    (r"Cinematic medium-full shot", "真人实拍中全景"),
    (r"Cinematic medium-long shot", "真人实拍中远景"),
    (r"Cinematic medium close-up", "真人实拍中近景"),
    (r"Cinematic medium shot from the side", "真人实拍侧面中景"),
    (r"Cinematic medium shot", "真人实拍中景"),
    (r"Cinematic three-quarter close-up", "真人实拍四分之三侧近景"),
    (r"Cinematic frontal close-up", "真人实拍正面近景"),
    (r"Cinematic close-up from an oblique side", "真人实拍斜侧近景"),
    (r"Cinematic close-up", "真人实拍近景"),
    (r"Cinematic tight close-up", "真人实拍大特写"),
    (r"Cinematic wide shot", "真人实拍全景"),
    (r"Cinematic long shot", "真人实拍远景"),
    (r"Cinematic insert", "真人实拍插入镜头"),
]

PHRASES: list[tuple[str, str]] = [
    ("locks only this person's face, build, and clothes, not the pose, not the background, not the composition",
     "只锁定这个人的脸、体型和衣服，不锁定姿势，不锁定背景，也不锁定构图"),
    ("locks only this woman's face, build, and clothes, not her pose, not the background, not the composition",
     "只锁定这个女人的脸、体型和衣服，不锁定她的姿势，不锁定背景，也不锁定构图"),
    ("locks only the woman's face, build, and clothes, not her pose, not the background, not the composition",
     "只锁定这个女人的脸、体型和衣服，不锁定她的姿势，不锁定背景，也不锁定构图"),
    ("locks only the man's face, build, and clothes, not his pose, not the background, not the composition",
     "只锁定这个男人的脸、体型和衣服，不锁定他的姿势，不锁定背景，也不锁定构图"),
    ("locks only the object's shape, not its place in the frame and not the composition",
     "只锁定这件东西的外形，不锁定它在画面里的位置，也不锁定构图"),
    ("locks only the space and materials, not the camera angle and not the composition",
     "只锁定空间和材质，不锁定机位，也不锁定构图"),
    ("locks only the shape of one bright yellow umbrella with clear ribs, not the composition",
     "只锁定一把明黄伞的外形和清楚的伞骨，不锁定构图"),
    ("locks only the shape of the bright yellow umbrella, not its place in the frame",
     "只锁定这把明黄伞的外形，不锁定它在画面里的位置"),
    ("locks only the riverside walk, the railing, and the river surface, not the camera position and not the composition",
     "只锁定河边步道、栏杆和河面，不锁定机位，也不锁定构图"),
    ("locks only the riverside walk, the railing, and the river surface, not the camera angle",
     "只锁定河边步道、栏杆和河面，不锁定机位"),
    ("locks only the phone's shape, not its place in the frame and not the composition",
     "只锁定这只手机的外形，不锁定它在画面里的位置，也不锁定构图"),
    ("is used only for a clean cuff, a shoulder, and a hand",
     "只用来锁定一只干净的袖口、一侧肩膀和一只手"),
    ("is used only for one hand", "只用来锁定一只手"),
    ("is used only for the hands", "只用来锁定双手"),
    ("is used only for one pair of hands", "只用来锁定一双手"),
    ("is used only for the other pair of hands", "只用来锁定另一双手"),
    ("is used only for the back and shoulder", "只用来锁定后背和肩膀"),
    ("is used only for the hands and the cuff", "只用来锁定双手和袖口"),
    ("is used only for one hand and the cuff", "只用来锁定一只手和袖口"),
    ("His face stays out of frame", "他的脸留在画外"),
    ("Her face stays out of the frame", "她的脸留在画外"),
    ("No face enters the frame", "不要有脸进入画面"),
    ("No face is in the frame", "画面里没有脸"),
    ("No recognizable face", "不要出现能认出的脸"),
    ("No other face is in the frame", "画面里不要再出现另一张脸"),
    ("Do not stretch them to the same height", "不要把两个人拉成一样高"),
    ("Keep her at about 170 cm and him at about 183 cm", "她大约一百七十厘米，他大约一百八十三厘米"),
    ("She is about 168 cm and he is about 183 cm", "她大约一百六十八厘米，他大约一百八十三厘米"),
    ("He is about 183 cm and she is about 168 cm", "他大约一百八十三厘米，她大约一百六十八厘米"),
    ("She is about 162 cm and he is about 183 cm", "她大约一百六十二厘米，他大约一百八十三厘米"),
    ("Not an athlete", "不是运动员的体格"),
    ("She is not an athlete", "她不是运动员的体格"),
    ("No paint", "身上没有颜料"),
    ("She has no paint", "她身上没有颜料"),
    ("There is no paint on her", "她身上没有颜料"),
    ("no paint", "没有颜料"),
    ("Do not veil the frame in gray fog", "不要把画面罩成灰雾"),
    ("Do not change the color of the clothes", "不要改衣服的颜色"),
    ("Do not change the color of her clothes", "不要改她衣服的颜色"),
    ("Do not change the color of their clothes", "不要改他们衣服的颜色"),
    ("and do not change the color of her clothes", "也不要改她衣服的颜色"),
    ("and do not change the color of their clothes", "也不要改他们衣服的颜色"),
    ("No teal-and-orange grade", "不要青橙色调"),
    ("No teal-and-orange", "不要青橙色调"),
    ("No scene numbers", "不要出现场号"),
    ("fine film grain", "细胶片颗粒"),
    ("photorealistic skin with visible pores and natural subsurface scattering",
     "真人皮肤，毛孔可见，有自然的次表面散射"),
    ("photorealistic", "真人实拍"),
    ("No morphing, no facial drift, no clothing changes", "不要变形，不要五官漂移，不要换衣服"),
    ("No morphing, no person entering, no change of place", "不要变形，不要有人走进来，不要换地方"),
    ("Fluid natural motion, realistic physics, 24fps", "动作自然，物理真实，每秒二十四帧"),
    ("Fluid natural motion, realistic rain, 24fps", "动作自然，雨是真实的，每秒二十四帧"),
    ("The motion is fluid and natural, with realistic physics, at 24fps", "动作自然，物理真实，每秒二十四帧"),
    ("Motion is fluid and natural, with realistic physics, at 24fps", "动作自然，物理真实，每秒二十四帧"),
    ("Fluid natural rain, realistic water, 24fps", "雨是自然的，水是真实的，每秒二十四帧"),
    ("No melody, no musical pads", "不要旋律，不要垫乐"),
    ("No text, no watermark, no logo", "不要另加文字，不要水印，不要标志"),
    ("No text other than", "除了屏幕上这一句，不要另加文字"),
    ("Do not reverse onto the camera owner's face", "不要反拍到主观镜头主人的脸"),
    ("This view does not reverse onto the camera owner's face", "这个视点不要反拍到镜头主人的脸"),
    ("Do not paint an interface on the back of the phone", "不要把界面画在手机背壳上"),
    ("Do not paint the interface on the back of the phone", "不要把界面画在手机背壳上"),
    ("Do not paint the interface on the outside of the headband", "不要把界面画在头带外壳上"),
    ("The screen is not painted on the phone's back", "屏幕不要画在手机背壳上"),
    ("It does not paint the interface onto the back of the phone", "不要把界面画到手机背壳上"),
    ("This frame shows the screen, not the back", "这一镜拍的是屏幕，不是背壳"),
    ("This shot shows only the screen face", "这一镜只拍屏幕这一面"),
    ("The frame shows that screen face", "画面拍的是屏幕这一面"),
    ("The screen faces the camera", "屏幕朝向镜头"),
    ("locked off with a sway of less than one degree, not handheld", "固定机位，晃动小于一度，不是手持"),
    ("locked off", "固定机位"),
    ("no pan and no push-in", "不摇，不推"),
    ("no push-in", "不推"),
    ("no zoom", "不拉焦距"),
    ("not handheld", "不是手持"),
    ("a slight handheld shake", "轻微手持晃动"),
    ("16:9", "16:9"),
    ("head height", "头高"),
    ("eye level", "眼高"),
    ("chest height", "胸高"),
    ("table height", "桌高"),
    ("hand height", "手高"),
    ("looking down", "俯拍"),
    ("The eye lands first on", "眼睛先落在"),
    ("The eye lands on", "眼睛落在"),
    ("The eye goes first to", "眼睛先落到"),
    ("Where eyes are visible, she blinks naturally", "能看见眼睛的时候，她自然地眨眼"),
    ("Where eyes are visible, they blink naturally", "能看见眼睛的时候，他们自然地眨眼"),
    ("Where his eyes show, he blinks naturally and does not hold his eyes open", "能看见他眼睛的时候，他自然地眨眼，不要一直睁着"),
    ("Where her eyes show, she blinks naturally and does not hold her eyes open", "能看见她眼睛的时候，她自然地眨眼，不要一直睁着"),
    ("Where the eyes are visible, they blink naturally, not held open", "能看见眼睛的时候自然地眨眼，不要一直睁着"),
    ("Where eyes are visible, they blink naturally and are not held open", "能看见眼睛的时候自然地眨眼，不要一直睁着"),
    ("Her eyes blink naturally, not held open", "她的眼睛自然地眨眼，不要一直睁着"),
    ("His eyes blink naturally, not held open", "他的眼睛自然地眨眼，不要一直睁着"),
    ("Their eyes blink naturally, not held open", "他们的眼睛自然地眨眼，不要一直睁着"),
    ("Her eyes blink naturally and are not held open", "她的眼睛自然地眨眼，不要一直睁着"),
    ("His eyes blink naturally and are not held open", "他的眼睛自然地眨眼，不要一直睁着"),
    ("Their eyes blink naturally and are not held open", "他们的眼睛自然地眨眼，不要一直睁着"),
    ("Both women blink naturally, and their eyes are not held open", "两个女人都自然地眨眼，眼睛不要一直睁着"),
    ("Anyone whose eyes are visible blinks naturally, and the eyes are not held open", "能看见眼睛的人都自然地眨眼，不要一直睁着"),
    ("If her eyes are visible, they blink naturally and are not held open", "如果能看见她的眼睛，就自然地眨眼，不要一直睁着"),
    ("Her eyes do not blink", "她的眼睛不眨"),
    ("His eyes do not blink", "他的眼睛不眨"),
    ("He does not blink, and he does not flinch", "他不眨眼，也不躲"),
    ("screen left", "画面左侧"),
    ("screen right", "画面右侧"),
    ("the left edge of the frame", "画面左边缘"),
    ("the right edge of the frame", "画面右边缘"),
    ("the lower edge of the frame", "画面下边缘"),
    ("the upper edge of the frame", "画面上边缘"),
    ("from the viewer's left to the viewer's right", "从观众的左侧到观众的右侧"),
    ("from the viewer's right to the viewer's left", "从观众的右侧到观众的左侧"),
    ("toward screen right", "朝画面右侧"),
    ("toward screen left", "朝画面左侧"),
    ("on screen left", "在画面左侧"),
    ("on screen right", "在画面右侧"),
    ("Maintain perfect consistency throughout —", "从头到尾保持一致："),
    ("Maintain the same umbrella shape, rib pattern, and yellow throughout", "伞的形状、伞骨和黄色从头到尾保持不变"),
    ("Lighting:", "光："),
    ("Color grade:", "色彩："),
    ("Sound is", "声音是"),
    ("no dialogue", "没有对白"),
    ("No dialogue", "没有对白"),
    ("No speech", "没有人说话"),
    ("No voice", "没有人声"),
    ("No mouth", "不要出现嘴"),
    ("room tone", "房间底噪"),
    ("and the spoken line", "以及说出来的那句台词"),
    ("and her spoken line", "以及她说出来的那句台词"),
    ("and his spoken line", "以及他说出来的那句台词"),
    ("and her laugh", "以及她的笑"),
    ("and her one line", "以及她的那一句"),
    ("heavy rain only", "只有暴雨"),
    ("heavy rain", "暴雨"),
    ("slightly muffled", "略闷"),
    ("Duration ", "时长"),
    (" seconds.", "秒。"),
    ("a light-gray brightness", "浅灰亮度"),
    ("a deep-gray brightness", "深灰亮度"),
    ("a near-black brightness", "接近全黑的亮度"),
    ("light-gray brightness", "浅灰亮度"),
    ("deep-gray brightness", "深灰亮度"),
    ("near-black brightness", "接近全黑的亮度"),
    ("white high brightness", "白的高亮度"),
    ("stays at a light-gray brightness", "保持浅灰亮度"),
    ("stays at a deep-gray brightness", "保持深灰亮度"),
    ("stays a light-gray brightness", "保持浅灰亮度"),
    ("stays a deep-gray brightness", "保持深灰亮度"),
    ("muted saturation, moderate contrast", "饱和度压低，反差中等"),
    ("higher saturation and stronger contrast in this shot", "这一镜饱和度更高，反差更强"),
    ("No slow motion", "不要慢动作"),
    ("The camera does not move at all", "摄影机完全不动"),
    ("The camera does not move", "摄影机不动"),
    ("The camera does not push in", "镜头不推近"),
    ("The camera does not pan", "镜头不摇"),
    ("The camera does not follow", "镜头不跟"),
    ("at a normal pace", "用正常语速"),
    ("at normal pace", "用正常语速"),
    ("with no word stressed", "没有哪一个词加重"),
    ("with no stressed word", "没有哪一个词加重"),
    ("with stress only on", "只重读"),
    ("with the stress only on", "只重读"),
    ("with the single stress on", "只重读"),
    ("Her mouth stays closed", "她的嘴闭着"),
    ("His mouth stays closed", "他的嘴闭着"),
    ("her mouth stays closed", "她的嘴闭着"),
    ("his mouth stays closed", "他的嘴闭着"),
    ("No mouth is in the frame", "画面里没有嘴"),
    ("while her mouth stays closed", "这期间她的嘴闭着"),
    ("While that voice speaks, her mouth stays closed", "画外那句说的时候，她的嘴闭着"),
    ("While that voice speaks, the man in frame does not open his mouth, and his lips stay closed", "画外那句说的时候，画面里的男人不开口，嘴唇闭着"),
    ("A voice off camera says", "一个画外的声音说"),
    ("An off-screen voice speaks", "一个画外的声音说"),
    ("An offscreen man speaks", "一个画外的男人说"),
    ("An offscreen woman speaks", "一个画外的女人说"),
    ("an offscreen man speaks", "一个画外的男人说"),
    ("an offscreen woman speaks", "一个画外的女人说"),
    ("Her voice speaks", "她的声音说"),
    ("She speaks", "她说"),
    ("He speaks", "他说"),
    ("She says", "她说"),
    ("He says", "他说"),
    ("She then speaks", "然后她说"),
    ("He then speaks", "然后他说"),
    ("She speaks again", "她再说"),
    ("He speaks again", "他再说"),
    ("She speaks first", "她先说"),
    ("He speaks first", "他先说"),
    ("The person in the gray smock speaks", "穿灰刷手服的人说"),
    ("the person in the gray smock speaks", "穿灰刷手服的人说"),
    ("the person in the gray smock", "穿灰刷手服的人"),
    ("in a firm tone", "语气坚定"),
    ("in a factual tone", "语气像在陈述事实"),
    ("in a warm, denying tone", "语气热络，却在否认"),
    ("in a calm catalog-note tone", "语气平静，像在念图录说明"),
    ("in the tone of someone assigning a seat", "语气像在指定座位"),
    ("in the tone of someone handing over goods", "语气像在交付一件东西"),
    ("in the tone of someone denying a claim", "语气像在拒赔"),
    ("in the tone of someone reading instructions", "语气像在念说明"),
    ("in the tone of someone asking about a claims clause", "语气像在问一条理赔条款"),
    ("in a courteous tone that smooths the room over in public", "语气客气，当众把这件事抹平"),
    ("in the tone of the procedure itself", "语气就是程序本身"),
    ("in the tone of a procedural decision", "语气像在宣布一项程序决定"),
    ("in the tone of a daughter speaking", "语气是女儿在说话"),
    ("in a tone that cuts the bidding off", "语气把报价截断"),
    ("in an ordinary speaking tone", "就是平常说话的语气"),
    ("in a low tone", "声音放低"),
    ("in a cool and exact tone", "语气冷，把话说准"),
    ("in a testing tone", "语气是在试探"),
    ("in a tone that states a price", "语气像在给一个价钱"),
    ("in a tone that hands the time back to him", "语气把时间交还给他"),
    ("in that same tone", "还是这个语气"),
    ("in a tone that gives it back", "语气把这件事还回去"),
    ("in a tone that states a choice", "语气像在做出选择"),
    ("in a tone that sets both outcomes down plainly", "语气把两种后果平平地放下"),
    ("in a tone that hands the question over", "语气把这个问题交出去"),
    ("in a tone that states a fact of touch", "语气像在陈述摸到的事实"),
    ("like a diagnosis", "像一句诊断"),
    ("like closing a case", "像在结案"),
    ("as if stating terms", "像在列出条件"),
    ("as if reading out a claim denial", "像在宣读拒赔"),
    ("as if he genuinely does not know", "像是他真的不知道"),
    ("as if he genuinely does not understand", "像是他真的不明白"),
    ("as if admitting he has failed", "像在承认自己没找到"),
    ("as if handing over evidence", "像在把证据交出去"),
    ("as if turning the claim of ownership back on her", "像把所有权这句问回给她"),
    ("as if talking about a living person", "像在说一个还活着的人"),
    ("as if asking about a living person", "像在问一个还活着的人"),
    ("as if he is really asking", "像是他真的在问"),
    ("as if there is no other way through", "像是没有别的人可以问"),
    ("in the tone of a prohibition", "语气是一句禁止"),
    ("in a command", "是一句命令"),
    ("recognizing the name and not greeting a reunion", "认出这个名字，不是重逢时的招呼"),
    ("bewildered", "茫然"),
    ("mechanical", "机械"),
    ("polite and blank", "客气，却是空的"),
    ("as if checking a fact", "像在核对一件事实"),
    ("refusing that explanation", "不接受这个解释"),
    ("still in the tone of someone handing over goods", "还是交付东西的语气"),
    ("the words coming through her teeth", "话从牙缝里出来"),
    ("like someone teaching a craft", "像在教一门手艺"),
    ("stating a secret as a plain fact", "把一个秘密说成一句平白的事实"),
    ("warm and firm", "热，并且拿得住"),
    ("in a calm, certain tone", "语气平静，很确定"),
    ("with the voice held down", "声音压低"),
    ("the tone a laugh still in the rain", "语气里还带着雨中的笑"),
    ("stress only on the word river", "只重读 river 这个词"),
    ("A woman, 31, about 168 cm, lean, narrow shoulders",
     "一个女人，三十一岁，大约一百六十八厘米，偏瘦，肩窄"),
    ("She is a woman, 31, about 168 cm, lean, narrow shoulders, in a work cardigan, with a lanyard badge reading ⟦",
     "她是一个女人，三十一岁，大约一百六十八厘米，偏瘦，肩窄，工装开衫，颈上挂着工牌，字是⟦"),
    ("Work cardigan, a lanyard badge reading", "工装开衫，颈上的工牌写着"),
    ("and reading glasses", "还有阅读镜"),
    ("reading glasses", "阅读镜"),
    ("in a work cardigan", "穿着工装开衫"),
    ("the badge off, the reading glasses off, not a black evening dress",
     "工牌已摘，阅读镜可摘，不是晚礼黑裙"),
    ("He is a man, 54, about 183 cm, lean face, clear cheekbones, veins on the hands, dried paint in the nails, painting clothes, a little softness at the waist, long frame",
     "他是一个男人，五十四岁，大约一百八十三厘米，脸瘦，颧骨清楚，手背有筋，指甲缝里是干颜料，穿着画画的衣服，腰腹略松，骨架仍长"),
    ("She is 34, about 170 cm, lean, fine wrists, ordinary dry clothes, paint on the left wrist",
     "她三十四岁，大约一百七十厘米，偏瘦，手腕细，衣服是普通的干衣服，左腕沾着颜料"),
    ("She is 34, about 170 cm, lean, fine wrists, paint on the wrist, ordinary clothes now wet from the rain",
     "她三十四岁，大约一百七十厘米，偏瘦，手腕细，腕上有颜料，普通衣服已经被雨打湿"),
    ("He is 34, about 183 cm, broad shoulders, neat dry clothes, no paint",
     "他三十四岁，大约一百八十三厘米，肩宽，衣服整洁而且是干的，没有颜料"),
    ("He is 34, about 183 cm, broad shoulders, narrow waist, neat clothes, a clean cuff, no paint",
     "他三十四岁，大约一百八十三厘米，肩宽腰细，衣服整洁，袖口干净，没有颜料"),
    ("It is a clear box holding a black glass spindle, a thin silver headband, and a small sealed envelope",
     "这是一只透明盒，里面是一枚黑色玻璃纺锤、一条银色薄头带和一只封口小信封"),
    ("It is a thin silver headband", "这是一条银色薄头带"),
    ("It is a contemporary candybar phone", "这是一只当代直板手机"),
    ("It is a contemporary bar phone", "这是一只当代直板手机"),
    ("It is one black glass spindle about the size of a knuckle", "这是一枚指节大小的黑色玻璃纺锤"),
    ("It is a bright yellow umbrella with clear ribs", "这是一把伞骨清楚的明黄伞"),
    ("One girl's hand, about eleven, lean", "一只大约十一岁女孩的手，偏瘦"),
    ("It is a dark viewing booth with a padded chair and an interface", "这是一间暗的观影舱，有软垫椅和一块界面"),
    ("It is a dark bathroom sink", "这是一只暗处的浴室水槽"),
    ("It is an emptied garment-loft studio at night: high windows, pale hang marks, an iron freight door, a work table, an easel, and a stove clock reading",
     "这是夜间一间大半搬空的旧服装阁楼：高窗、浅色挂痕、一扇货梯铁门、一张工作台、一个画架，炉上的钟读作"),
    ("The space is a champagne-lit gallery of white paintings with a small red dot near each edge and one wall empty",
     "这是香槟灯光下的画廊，白墙上是一排白画，每幅靠边缘有一点小红，有一面墙是空的"),
    ("She is in that crowd", "她在那个人群里"),
    ("She is in that booth", "她在这间舱里"),
    ("Use this room", "就用这个房间"),
    ("Do not invent a different room", "不要另造一间房间"),
    ("A hand comes in from the lower right edge of the frame", "一只手从画面右下边缘伸进来"),
    ("warm summer rain", "暖的夏日暴雨"),
    ("The river is not green in this shot", "这一镜的河不要拍成绿色"),
    ("the river is not green in this shot", "这一镜的河不要拍成绿色"),
    ("Do not let green water fill the frame", "不要让绿色的水铺满画面"),
    ("No kiss, no slow motion", "不要接吻，不要慢动作"),
    ("The river surface is not the subject, and the river is not green in this shot",
     "河面不是这一镜的主体，这一镜的河也不要拍成绿色"),
    ("No clear face as the subject", "不要让清楚的人脸成为主体"),
    ("No sunny day", "不要晴天"),
    ("The water does not turn any color other than green", "水不要变成绿色以外的颜色"),
    ("slightly warm", "略暖"),
    ("under the umbrella the brightness stays deep gray and slightly warm", "伞下的亮度保持深灰，略暖"),
    ("The raindrops are brighter than the shade beneath the umbrella", "雨滴比伞下更亮"),
    ("side-back light on her stays a light-gray brightness", "打在她身上的侧逆光保持浅灰亮度"),
    ("The slanting rain is brighter than she is", "斜着落下的雨比她更亮"),
    ("He, under the umbrella, stays deep gray", "伞下的他保持深灰"),
    ("side-back light on both of them stays a light-gray brightness", "打在两个人身上的侧逆光保持浅灰亮度"),
    ("the water stays brighter than the bank and stays green", "水面比岸更亮，并且保持绿色"),
    ("The bank stays a deep-gray brightness", "岸保持深灰亮度"),
    ("Do not change the green", "不要把绿色改掉"),
    ("rain-lit green on the water, deep gray on the bank", "雨光把水面打成绿色，岸是深灰"),
    ("No science-fiction color", "不要科幻色"),
    ("the light on the hand stays a light-gray brightness", "打在手上的光保持浅灰亮度"),
    ("The yellow umbrella is brighter than the hand and stays yellow", "黄伞比手更亮，并且保持黄色"),
    ("Do not change the yellow of the umbrella", "不要改黄伞的黄色"),
    ("rain light and a bright yellow umbrella", "雨光和一把明亮的黄伞"),
    ("Gray smock", "灰刷手服"),
    ("A gray smock", "一件灰刷手服"),
    ("The face is not memorable", "这张脸不必被人记住"),
    ("A white buyer-counter room", "一间白墙白光的买方柜台房间"),
    ("The woman is about 168 cm", "这个女人大约一百六十八厘米"),
    ("The other person keeps the height in", "另一个人的身高以"),
    ("Image ", "图"),
]


def apply_phrases(text: str) -> str:
    for src, dst in PHRASES:
        text = text.replace(src, dst)
    text = re.sub(r"(\d+)mm lens", lambda m: cn_mm(m.group(1)), text)
    text = re.sub(r"\bShe\b", "她", text)
    text = re.sub(r"\bHe\b", "他", text)
    text = re.sub(r"\bHer\b", "她的", text)
    text = re.sub(r"\bHis\b", "他的", text)
    text = re.sub(r"\bThey\b", "他们", text)
    text = re.sub(r"\bTheir\b", "他们的", text)
    text = text.replace("声音是只有", "声音只有")
    text = text.replace("声音是暴雨以及", "声音是暴雨，以及")
    return text


def translate_paste(paste: str) -> str:
    protected, vault = protect(paste)
    for src, dst in SHOT:
        protected = protected.replace(src, dst)
    protected = apply_phrases(protected)
    return restore(protected, vault).strip()


def main() -> None:
    text = ROOT.read_text()
    # structural
    text = text.replace(
        "日期：2026年10月7日（按分镜与剧本重写可贴入）",
        "日期：2026年10月8日（可贴入改为中文，并按分镜与剧本改正动作）",
    )
    text = text.replace(
        "每条含 **分镜对照**（给人看，保留人名和机位号）和 **可贴入**（英文七段，装在代码块里：镜头、素材锁定、这一镜的动作、Lighting、Color grade、一致性、时长与声音）。",
        "每条含 **分镜对照**（给人看，保留人名和机位号）和 **可贴入**（中文整段，装在代码块里：时长与画幅、素材锁定、这一镜的动作、光、色彩、一致性、声音）。",
    )
    text = text.replace(
        "- **画质意图：** 真人实拍。可贴入以 Cinematic 起句，写明景别和焦距。不要另堆 8K、大师级。",
        "- **画质意图：** 真人实拍。可贴入用中文写明景别和焦距。不要另堆 8K、大师级。",
    )
    text = text.replace(
        "- **上传：** 每条最多 9 张图。按下条「素材」顺序上传；**素材行**可写内部代号（P-/L-/A-）供人对表。**可贴入**用 Image 1、Image 2，与素材行的图1、图2一一对应，不写代号，不写剧本人名与场景专名。",
        "- **上传：** 每条最多 9 张图。按下条「素材」顺序上传；**素材行**可写内部代号（P-/L-/A-）供人对表。**可贴入**用图1、图2，与素材行一一对应，不写代号，不写剧本人名与场景专名。",
    )
    text = text.replace(
        "- **可贴入指代：** 人物、地点、英雄道具在句中用 Image N 指认。**禁止**在可贴入里出现 Claire、Gabriel、Naomi、Margot、White Room、交易所、公寓名等仅剧本/附件才有的标签。例外：**台词与屏幕/道具上必须读出的原文**（英文对白、`G. Mora` 等）保留原文。",
        "- **可贴入指代：** 人物、地点、英雄道具在句中用图N指认。**禁止**在可贴入里出现 Claire、Gabriel、Naomi、Margot、White Room、交易所、公寓名等仅剧本/附件才有的标签。例外：**台词与屏幕/道具上必须读出的原文**保留原文。",
    )
    text = text.replace(
        "- **机位代号：** 分镜索引与 **分镜对照** 里的 D1、D2… 是本项目机位注册编号，供摄影组对表；**可贴入** 不写 D#，改用景别、机高、焦距毫米、运镜与 Image N。",
        "- **机位代号：** 分镜索引与 **分镜对照** 里的 D1、D2… 是本项目机位注册编号，供摄影组对表；**可贴入** 不写 D#，改用景别、机高、焦距毫米、运镜与图N。",
    )
    text = text.replace(
        "- **焦距：** 每条都锁定一个具体毫米数，来自分镜机位注册表的允许范围，再按景别取定点。提示词写 `85mm lens, no zoom` 这种定点，不要写变焦，也不要写 24–35mm 这种范围。",
        "- **焦距：** 每条都锁定一个具体毫米数，来自分镜机位注册表的允许范围，再按景别取定点。提示词写「八十五毫米，不拉焦距」这种定点，不要写变焦，也不要写范围。",
    )
    text = text.replace(
        "| A-Note     | 抖动手写两行：`You have one sentence.` / `Tell Naomi the red dot is hers.` |",
        "| A-Note     | 抖动手写两行：`你有一句话。` / `告诉 Naomi，红点是她的。`                   |",
    )
    text = text.replace("| 5A 工作室对峙     | 5A.1–5A.40  | 40      |", "| 5A 工作室对峙     | 5A.1–5A.40（无 5A.10、5A.21） | 38 |")
    text = text.replace("| **合计**          |             | **169** |", "| **合计**          |             | **167** |")

    # 1.2 对照与不要做
    text = text.replace(
        "0:03–0:06 Claire 向画右半步，Gabriel 手从画左伸入将扣腕。",
        "0:03–0:06 Claire 向画右迈出很小的一步，伸手抓住 Gabriel 的手，把他往雨里带。他不拿伞。",
    )
    text = text.replace(
        "- **人物动作** Claire 中速带笑；Gabriel 伞下不动只伸手。",
        "- **人物动作** Claire 中速带笑，伸手抓住 Gabriel 的手；Gabriel 在伞下，不拿伞，被她拽向雨。",
    )
    text = text.replace(
        "**不要做：** 不要让图4的手碰到或抓住手腕；不要露出图4的正脸；不要让图4走进雨里；不要拥抱；不要把图1的脸拍成满框；不要推近。",
        "**不要做：** 不要让图4拿着伞；不要露出图4的正脸；不要让图4自己走进雨里；不要停在指尖靠近却不抓住；不要拥抱；不要把图1的脸拍成满框；不要推近。",
    )
    text = text.replace(
        "**素材：** 图1＝P-Naomi-31；图2＝P-Attendant；图3＝L-Counter。\n\n**可贴入：**\n\n```text\nCinematic wide two-shot",
        "**素材：** 图1＝P-Naomi-31；图2＝P-Attendant；图3＝L-Counter；图4＝A-Box。\n\n**可贴入：**\n\n```text\nCinematic wide two-shot",
    )
    text = text.replace(
        "**素材：** 图1＝A-WRI；图2＝L-Kitchen；图3＝P-Claire-36。",
        "**素材：** 图1＝A-WRI；图2＝L-Kitchen；图3＝P-Claire-36；图4＝P-Naomi-13。",
    )

    # drop standalone shots the storyboard no longer has
    text = re.sub(
        r"\n### 5A\.10　8秒　七十五毫米　全能参考　16:9\n.*?(?=\n### 5A\.11　)",
        "\n",
        text,
        count=1,
        flags=re.S,
    )
    text = re.sub(
        r"\n### 5A\.21　9秒　六十五毫米　全能参考　16:9\n.*?(?=\n### 5A\.22　)",
        "\n",
        text,
        count=1,
        flags=re.S,
    )
    text = text.replace("### 5A.22　10秒　四十毫米", "### 5A.22　14秒　四十毫米")

    def repl_paste(m: re.Match) -> str:
        block = m.group(0)
        # shot id is looked up from preceding heading via closure? we'll translate all pastes in a second pass
        return block

    # translate each paste, with shot id from the nearest heading above
    pieces = []
    pos = 0
    for m in re.finditer(r"```text\n(.*?)```", text, flags=re.S):
        heading = text.rfind("\n### ", 0, m.start())
        sid = ""
        if heading != -1:
            hm = re.match(r"\n### ([0-9][0-9A-Z.]*M?)", text[heading:])
            if hm:
                sid = hm.group(1)
        paste = fix_shot(sid, m.group(1))
        zh = translate_paste(paste)
        pieces.append(text[pos:m.start()])
        pieces.append("```text\n" + zh + "\n```")
        pos = m.end()
    pieces.append(text[pos:])
    out = "".join(pieces)
    ROOT.write_text(out)
    # leftover report
    left = collections_english(out)
    report = Path("/Users/vimchain/Obsidian/Screenplays/The Pain We Sell/.cursor/h3-leftover.txt")
    report.write_text("\n".join(f"{n:4} {w}" for w, n in left.most_common(120)))
    print("leftover kinds", len(left), "top", left.most_common(25))


def collections_english(text: str):
    import collections
    body = []
    for m in re.finditer(r"```text\n(.*?)```", text, flags=re.S):
        chunk = re.sub(r"`[^`]*`|\"[^\"]*\"", "", m.group(1))
        body.append(chunk)
    words = re.findall(r"[A-Za-z][A-Za-z']{3,}", "\n".join(body))
    return collections.Counter(w for w in words if w not in {"fps"})


def fix_shot(sid: str, paste: str) -> str:
    if sid == "1.2":
        paste = paste.replace(
            "At the same time his hand comes in from the left edge of the frame toward her wrist. The fingertips come close and stop before they touch skin. Where eyes are visible, she blinks naturally.",
            "At the same time she reaches to his hand, takes it, and pulls him toward the rain. He does not hold the umbrella, and his hand does not reach for her. Where eyes are visible, she blinks naturally.",
        )
        paste = paste.replace("His hand never touches or grabs. ", "She does take his hand. He does not hold the umbrella. ")
        paste = paste.replace(
            "He stays under the umbrella, rear of screen left, only the cuff and shoulder visible, standing still.",
            "He stays at the rear of screen left, under the umbrella but not holding it, only the cuff and shoulder visible.",
        )
    elif sid == "2.2":
        paste = paste.replace(
            "She holds still. The badge, the reading glasses, and the highlighter cap bitten in her mouth share the same frame. The eye lands first on the cap in her mouth.",
            "She turns the pages of one report, and her finger stops on one line. She lays the report flat, and her gaze drops to the handwritten timeline. The badge, the reading glasses, and the highlighter cap bitten in her mouth stay in the same frame. The eye lands first on the cap in her mouth.",
        )
    elif sid == "2.3":
        paste = paste.replace(
            "The red frame holds the two circles. `12 MIN?` stays in the center of the page. The eye lands first on the two circles.",
            "The red frame holds the two circles `12:22` and `12:34`. `12 MIN?` stays in the center of the page. A hand holds a highlighter, and the tip taps once in the gap between the two circles, then stops. The eye lands first on the two circles.",
        )
    elif sid == "2.4":
        paste = paste.replace(
            "The lit phone lies on the center of the file and vibrates. The eye lands first on the moving phone. The glass stays bright and does not need readable lines.",
            "The lit phone lies on the center of the file and vibrates. A hand comes in from the right edge of the frame and the fingertips press the phone's edge until it stops shifting. The eye lands first on the moving phone. The glass stays bright and does not need readable lines.",
        )
    elif sid == "2.5":
        paste = paste.replace(
            "`定向竞买成交 — 标的 7186 — 卖方 G. Mora — 买方 Naomi Bennett（唯一获准竞买人）`",
            "`定向竞买成交 — 标的 7186 — 卖方 G. Mora — 标的 Claire Bennett（已故 — 无需本人同意）`",
        )
    elif sid == "2.6":
        paste = paste.replace(
            "Over the shoulder, an old message fills the readable area with `Tonight. Come.`. Any face stays a dark foreground, not recognizable, and not as sharp as the words. The eye lands first on `Tonight. Come.`.",
            "Over the shoulder, the readable area first shows `Tonight. Come.`. Then the line above it, `I won't clap for him.`, enters the readable area. Any face stays a dark foreground, not recognizable, and not as sharp as the words. The eye lands first on `Tonight. Come.`.",
        )
    elif sid == "3.1":
        paste = paste.replace(
            "The other person keeps the height in Image 2. Do not stretch them to the same height.",
            "The other person keeps the height in Image 2. Do not stretch them to the same height. Image 4 locks only the object's shape, not its place in the frame and not the composition. It is a clear box holding a black glass spindle, a thin silver headband, and a small sealed envelope.",
        )
        paste = paste.replace(
            "White walls and white light press both people onto the same flat plane. The eye lands first on the gray smock.",
            "White walls and white light press both people onto the same flat plane. The person in the gray smock lifts the clear box onto the counter and pushes it across the counter toward the woman. The black spindle, the silver headband, and the sealed envelope stay visible inside the box. The eye lands first on the gray smock.",
        )
    elif sid == "4.1":
        paste = paste.replace("the date `06/11` in focus", "the date line `06/11 -- 开幕夜 -- 3:48:10` in focus")
        paste = paste.replace(
            "After it sits, the index stops, and the date `06/11` rests alone in the center of the interface. The other entries are not left on the screen. The eye lands on that date.",
            "After it sits, the index stops on the line `06/11 -- 开幕夜 -- 3:48:10`, and that full line rests in the center of the interface. The eye lands on that line.",
        )
    elif sid == "4.3":
        paste = paste.replace(
            "Her body hits the wall and stays on the right side of the frame. The eye lands on the headband leaving her head. Any interface in the frame shows only an index, a filename, a progress mark, and abstract light, and it does not show a recognizable memory image. Her eyes blink naturally and are not held open.",
            "Her body hits the wall on the right side of the frame and slides a short way down until her back stays against the wall. The eye lands on the headband leaving her head. Any interface in the frame shows only an index, a filename, a progress mark, and abstract light, and it does not show a recognizable memory image. Her eyes stay open and do not blink.",
        )
    elif sid == "4.7M":
        paste = paste.replace(
            "The hand holds a small piece of paper. The flame licks the fingers first. Ash falls. Water runs only after the ash has fallen. The eye lands on the flame.",
            "The hand holds a small piece of paper. The flame licks the fingers first. Ash falls. Water runs only after the ash has fallen. Only then does the hand go into a pocket to take out a phone. The phone screen is not shown. The eye lands on the flame.",
        )
    elif sid == "4.8":
        paste = paste.replace(
            "Her wet face stays still. Her gaze settles and stays in one place. The eye lands on her eyes. Her eyes blink naturally and are not held open.",
            "Her wet face stays still and she does not wipe it. Her eyes do not blink. Her gaze holds, then drops from straight ahead toward the interface, and her jaw draws in a little. The eye lands on her eyes.",
        )
    elif sid == "4.9":
        paste = paste.replace(
            "A finger draws a box around `3:36:02–3:48:10` on that interface. The eye lands on those start and end times. The rest of the index stays outside the box.",
            "A finger draws a box around `3:36:02–3:48:10` on that interface. The eye lands on those start and end times. The rest of the index stays outside the box. The thumb then stops above the save control and stays there.",
        )
    elif sid == "4.11":
        paste = paste.replace("`I have it... Nine AM.`", "`I have it. One Police Plaza. Nine AM.`")
    elif sid == "5A.3":
        paste = paste.replace(
            "A gray stroke travels from the viewer's right to the viewer's left",
            "A gray stroke travels from the viewer's left to the viewer's right",
        )
    elif sid == "5A.9":
        paste = paste.replace(
            "The eye goes first to that pulsing dot. No face enters the frame.",
            "The eye goes first to that pulsing dot. No face enters the frame. Near the end, a woman's voice from outside the frame says, at a normal pace, as if testing the figure, with stress only on \"thousand\": \"Forty-six thousand.\" No mouth is in the frame.",
        )
    elif sid == "5A.20":
        paste = paste.replace(
            "His eyes blink naturally, not held open. He speaks at a normal pace, as if he genuinely does not know, with no word stressed: \"I don't know.\"",
            "His eyes do not blink. He speaks at a normal pace, as if he genuinely does not know, with no word stressed: \"I don't know.\"",
        )
    elif sid == "5A.22":
        paste = paste.replace("Duration 10 seconds.", "Duration 14 seconds.")
        paste = paste.replace(
            "He speaks first, at a normal pace, as if he genuinely does not understand, stressing only the word \"what\": \"Beneficiary of what?\"",
            "She speaks first, at a normal pace, in the tone of someone denying a claim, stressing only the word \"deny\": \"I'd deny this claim in a minute. Twelve minutes. No explanation. One beneficiary.\" He then speaks, at a normal pace, as if he genuinely does not understand, stressing only the word \"what\": \"Beneficiary of what?\"",
        )
    elif sid == "5A.31":
        paste = paste.replace(
            "His eyes travel back and forth between the painting on the left of the frame and her soft shoulder on the right of the frame. They then stop in the empty space between those two.",
            "His eyes travel from the painting on the left of the frame, to her soft shoulder on the right of the frame, then to the gray canvas, and only then stop in the empty space between them.",
        )
    elif sid == "5B.3M":
        paste = paste.replace(
            "The silver-haired woman steps into the foreground in front of the woman in the black dress. The eye lands first on the silver hair. She speaks at a normal pace",
            "The silver-haired woman steps into the foreground, leans in, and kisses the woman in the black dress once on each cheek. The eye lands first on the silver hair. She then speaks at a normal pace",
        )
    elif sid == "5B.11M":
        paste = paste.replace(
            "Do not add a red dot.",
            "Do not add a red dot. Image 4 locks only this person's face, build, and clothes, not the pose, not the background, not the composition. She is a girl of about 13, about 145 cm, lean, with slightly long limbs and home clothes. She sits at the table inside the room, doing math, the tip of her tongue against a tooth.",
        )
        paste = paste.replace(
            "The woman stands beside it, inside the room. Her mouth stays closed.",
            "The woman stands beside the canvas, inside the room. The girl sits at the table in the same room, seen through the door. The woman's mouth stays closed.",
        )
    elif sid == "5B.16M":
        paste = paste.replace(
            "It is a large unfinished canvas of an empty room and a bed rail, with one red dot.",
            "It is a large unfinished canvas of an empty room and a bed rail, with no red dot yet.",
        )
        paste = paste.replace(
            "She stands the small board upright beside the large canvas. A gentle pan follows the board and stops when it is steady. The eye lands first on the two red dots. When the pan stops, the two red dots sit at the same height.",
            "She stands the small board upright beside the large canvas. The small board already has one red dot. The large canvas does not. A gentle pan follows the board and stops when the two surfaces sit at the same height. She then dips the brush and puts one small red dot on the large canvas at that same height. The eye lands first on the new dot.",
        )
    elif sid in {"5B.30M", "5B.31M"}:
        paste = paste.replace("`You have one sentence.`", "`你有一句话。`")
        paste = paste.replace("`Tell Naomi the red dot is hers.`", "`告诉 Naomi，红点是她的。`")
    elif sid == "6.4":
        paste = paste.replace(
            "His eyes blink naturally, not held open.",
            "His eyes do not blink.",
        )
    return paste


if __name__ == "__main__":
    main()
