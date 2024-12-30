from sqlalchemy.orm import Session
from models.power_model import Power
from models.province_model import Inland, Coast, Water


def generate_master_data(session: Session) -> None:
    powers = [
        Power(symbol="a", name="Austria", adjective="Austrian"),
        Power(symbol="e", name="England", adjective="English"),
        Power(symbol="f", name="France", adjective="French"),
        Power(symbol="g", name="Germany", adjective="German"),
        Power(symbol="i", name="Italy", adjective="Italian"),
        Power(symbol="r", name="Russia", adjective="Russian"),
        Power(symbol="t", name="Turkey", adjective="Turkish"),
    ]
    session.add_all(powers)
    session.commit()

    power_a = session.query(Power).filter_by(symbol="a").first()
    power_e = session.query(Power).filter_by(symbol="e").first()
    power_f = session.query(Power).filter_by(symbol="f").first()
    power_g = session.query(Power).filter_by(symbol="g").first()
    power_i = session.query(Power).filter_by(symbol="i").first()
    power_r = session.query(Power).filter_by(symbol="r").first()
    power_t = session.query(Power).filter_by(symbol="t").first()

    provinces = [
        Water(abbr="adr", name="Adriatic Water", jname="アドリア海"),
        Water(abbr="aeg", name="Aegean Water", jname="エーゲ海"),
        Coast(abbr="alb", name="Albania", jname="アルバニア"),
        Coast(abbr="ank", name="Ankara", jname="アンカラ", supply_center=True, region=power_t),
        Coast(abbr="apu", name="Apulia", jname="アプリア", region=power_i),
        Coast(abbr="arm", name="Armenia", jname="アルメニア", region=power_t),
        Water(abbr="bal", name="Baltic Water", jname="バルト海"),
        Water(abbr="bar", name="Barents Water", jname="バレンツ海"),
        Coast(abbr="bel", name="Belgium", jname="ベルギー", supply_center=True),
        Coast(abbr="ber", name="Berlin", jname="ベルリン", supply_center=True, region=power_g),
        Water(abbr="bla", name="Black Water", jname="黒海"),
        Inland(abbr="boh", name="Bohemia", jname="ボヘミア", region=power_a),
        Water(abbr="bot", name="Gulf of Bothnia", jname="ボスニア湾"),
        Coast(abbr="bre", name="Brest", jname="ブレスト", supply_center=True, region=power_f),
        Inland(abbr="bud", name="Budapest", jname="ブダペスト", supply_center=True, region=power_a),
        Coast(abbr="bul", name="Bulgaria", jname="ブルガリア", supply_center=True),
        Coast(abbr="bul_ec", name="Bulgaria(EC)", jname="ブルガリア(EC)"),
        Coast(abbr="bul_sc", name="Bulgaria(SC)", jname="ブルガリア(SC)"),
        Inland(abbr="bur", name="Burgundy", jname="ブルゴーニュ", region=power_f),
        Coast(abbr="cly", name="Clyde", jname="クライド", region=power_e),
        Coast(abbr="con", name="Constantinople", jname="コンスタンティノープル", supply_center=True, region=power_t),
        Coast(abbr="den", name="Denmark", jname="デンマーク", supply_center=True),
        Water(abbr="eas", name="Eastern Mediterranean", jname="東地中海"),
        Coast(abbr="edi", name="Edinburgh", jname="エディンバラ", supply_center=True, region=power_e),
        Water(abbr="eng", name="English Channel", jname="イギリス海峡"),
        Coast(abbr="fin", name="Finland", jname="フィンランド", region=power_r),
        Inland(abbr="gal", name="Galicia", jname="ガリツィア", region=power_a),
        Coast(abbr="gas", name="Gascony", jname="ガスコーニュ", region=power_f),
        Coast(abbr="gre", name="Greece", jname="ギリシア", supply_center=True),
        Water(abbr="hel", name="Helgoland Bight", jname="ヘルゴラント湾"),
        Coast(abbr="hol", name="Holland", jname="オランダ", supply_center=True),
        Water(abbr="ion", name="Ionian Water", jname="イオニア海"),
        Water(abbr="iri", name="Irish Water", jname="アイリッシュ海"),
        Coast(abbr="kie", name="Kiel", jname="キール", supply_center=True, region=power_g),
        Coast(abbr="lon", name="London", jname="ロンドン", supply_center=True, region=power_e),
        Coast(abbr="lvn", name="Livonia", jname="リヴォニア", region=power_r),
        Coast(abbr="lvp", name="Liverpool", jname="リヴァプール", supply_center=True, region=power_e),
        Water(abbr="lyo", name="Gulf of Lyon", jname="リオン湾"),
        Water(abbr="mao", name="Mid-Atlantic Ocean", jname="中大西洋"),
        Coast(abbr="mar", name="Marseilles", jname="マルセイユ", supply_center=True, region=power_f),
        Inland(abbr="mos", name="Moscow", jname="モスクワ", supply_center=True, region=power_r),
        Inland(abbr="mun", name="Munich", jname="ミュンヘン", supply_center=True, region=power_g),
        Coast(abbr="naf", name="North Africa", jname="北アフリカ"),
        Water(abbr="nao", name="North Atlantic Ocean", jname="北大西洋"),
        Coast(abbr="nap", name="Naples", jname="ナポリ", supply_center=True, region=power_i),
        Water(abbr="nth", name="North Water", jname="北海"),
        Water(abbr="nwg", name="Norwegian Water", jname="ノルウェー海"),
        Coast(abbr="nwy", name="Norway", jname="ノルウェー", supply_center=True),
        Inland(abbr="par", name="Paris", jname="パリ", supply_center=True, region=power_f),
        Coast(abbr="pic", name="Picardy", jname="ピカルディ", region=power_f),
        Coast(abbr="pie", name="Piedmont", jname="ピエモンテ", region=power_i),
        Coast(abbr="por", name="Portugal", jname="ポルトガル", supply_center=True),
        Coast(abbr="pru", name="Prussia", jname="プロイセン", region=power_g),
        Coast(abbr="rom", name="Rome", jname="ローマ", supply_center=True, region=power_i),
        Inland(abbr="ruh", name="Ruhrl", jname="ルール", region=power_g),
        Coast(abbr="rum", name="Rumania", jname="ルーマニア", supply_center=True),
        Inland(abbr="ser", name="Serbia", jname="セルビア", supply_center=True),
        Coast(abbr="sev", name="Sevastopol", jname="セヴァストポリ", supply_center=True, region=power_r),
        Inland(abbr="sil", name="Silesia", jname="シレジア", region=power_g),
        Water(abbr="ska", name="Skagerrak", jname="スカゲラク海峡"),
        Coast(abbr="smy", name="Smyrna", jname="スミルナ", supply_center=True, region=power_t),
        Coast(abbr="spa", name="Spain", jname="スペイン", supply_center=True),
        Coast(abbr="spa_nc", name="Spain(NC)", jname="スペイン(NC)"),
        Coast(abbr="spa_sc", name="Spain(SC)", jname="スペイン(SC)"),
        Coast(abbr="stp", name="St. Petersburg", jname="サンクトペテルブルク", supply_center=True, region=power_r),
        Coast(abbr="stp_nc", name="St. Petersburg(NC)", jname="サンクトペテルブルク(NC)"),
        Coast(abbr="stp_sc", name="St. Petersburg(SC)", jname="サンクトペテルブルク(SC)"),
        Coast(abbr="swe", name="Sweden", jname="スウェーデン", supply_center=True),
        Coast(abbr="syr", name="Syria", jname="シリア", region=power_t),
        Coast(abbr="tri", name="Trieste", jname="トリエステ", supply_center=True, region=power_a),
        Coast(abbr="tun", name="Tunis", jname="チュニス", supply_center=True),
        Coast(abbr="tus", name="Tuscany", jname="トスカーナ", region=power_i),
        Inland(abbr="tyr", name="Tyrolia", jname="ティロル", region=power_a),
        Water(abbr="tys", name="Tyrrhenian Water", jname="ティレニア海"),
        Inland(abbr="ukr", name="Ukraine", jname="ウクライナ", region=power_r),
        Coast(abbr="ven", name="Venice", jname="ヴェネツィア", supply_center=True, region=power_i),
        Inland(abbr="vie", name="Vienna", jname="ウィーン", supply_center=True, region=power_a),
        Coast(abbr="wal", name="Wales", jname="ウェールズ", region=power_e),
        Inland(abbr="war", name="Warsaw", jname="ワルシャワ", supply_center=True, region=power_r),
        Water(abbr="wes", name="Western Mediterranean", jname="西地中海"),
        Coast(abbr="yor", name="Yorkshire", jname="ヨークシャー", region=power_e),
    ]
    session.add_all(provinces)
    session.commit()
