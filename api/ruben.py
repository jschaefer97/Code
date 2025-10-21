#%% Spezialhandel

 

# # real vars - exports

lst = [

    "depric4691",  

    "depric4690",  

    "detrad0692",  

    "detrad0689",  

]

 

spezialhandel_data = utils.load_mb_bulk(lst)

spezialhandel_data.columns = ["sbk_exports_price_index","sbk_imports_price_index","sbk_exports","sbk_imports"]

 

preise_dest = spezialhandel_data.iloc[:,:2]

 

spezialhandel_data["rPVexports"] = spezialhandel_data.sbk_exports / spezialhandel_data.sbk_exports_price_index.shift(1) * 100

 

# real vars - imports

spezialhandel_data["rPVimports"] = spezialhandel_data.sbk_imports / spezialhandel_data.sbk_imports_price_index.shift(1) * 100

 

#%% PMI

 

ind_pmi = ["markit_3y_pmiglmanpm",

"markit_3y_pmiusmanmepm",

"markit_3y_pmiezmanpm",

"markit_3y_pmicnmanpm",

"markit_3y_pmidemanpm"]

ind_pmi = utils.load_mb_bulk(ind_pmi)

ind_pmi.columns = ["pmi_"+e for e in ["World","US","Euro Area","China","Germany"]]

 

ind_caputil = ["usprod1071",    

"euprod0507",  

"cnprod0910"]

ind_caputil = utils.load_mb_bulk(ind_caputil)

ind_caputil.columns = ["caputil_"+e for e in ["US","Euro Area","China"]]

 

ind_worldtrade = ["worldtrad0001","ih:mb:com:fd_wd_new"]

ind_worldtrade = utils.load_mb_bulk(ind_worldtrade)

ind_worldtrade.columns = ["World Trade","Foreign Demand (ih)"]

ind_worldtrade = ind_worldtrade.resample("M").mean().bfill()

 

indicator_dict = OrderedDict(zip(["ExpExportBusinessNext3Months","Assessment of ForeignOrders","NewOrders_exvehicle","NewOrdersEA_exvehicle","NewOrdersEA_majorders","foreignDemand"],["desurv1142","deifo_c0000000_xus_bdb","deprod2825","deprod2834","deprod2473"]))

ind_ifo = utils.load_mb_bulk(indicator_dict.values())

ind_ifo.columns = indicator_dict.keys()

 

indicator_dict = OrderedDict({

    "int5year_us":"us05ygov",  

    "int5year_de":"de5ygov",    

    "int5year_it":"it5ygov",    

})

ind_interest = utils.load_mb_bulk(indicator_dict.values())

ind_interest.columns = indicator_dict.keys()

 

 

# nowcast import / export

us_exp = utils.load_fred(["A253RX1Q020SBEA","EXPORTSGOODSNOW"],1990,2030)

us_exp.columns = ["exp","exp_nowcast"]

us_exp.exp_nowcast = us_exp.exp_nowcast/100

us_exp["US_EXP"] = utils.extrapolate_with_rates(us_exp.exp,us_exp.exp_nowcast)

 

us_imp = utils.load_fred(["A255RX1Q020SBEA","IMPORTSGOODSNOW"],1990,2030)

us_imp.columns = ["imp","imp_nowcast"]

us_imp.imp_nowcast = us_imp.imp_nowcast/100

us_imp["US_IMP"] = utils.extrapolate_with_rates(us_imp.imp,us_imp.imp_nowcast)

 

us_trade = pd.concat([us_exp.US_EXP,us_imp.US_IMP],axis=1)

 

dl_series = OrderedDict({
    "Total":{
        "ex":"M.N.DE.W1.S1.S1.T.C.S._Z._Z._Z.EUR._T._X.N.ALL",
        "im":"M.N.DE.W1.S1.S1.T.D.S._Z._Z._Z.EUR._T._X.N.ALL",
    },

    "Fertigungsleistungen":{
        "ex":"M.N.DE.W1.S1.S1.T.C.SA._Z._Z._Z.EUR._T._X.N.ALL",
        "im":"M.N.DE.W1.S1.S1.T.D.SA._Z._Z._Z.EUR._T._X.N.ALL",
        },

    "Transportleistungen":{
        "ex":"M.N.DE.W1.S1.S1.T.C.SC._Z._Z._Z.EUR._T._X.N.ALL",
        "im":"M.N.DE.W1.S1.S1.T.D.SC._Z._Z._Z.EUR._T._X.N.ALL",
        },

    "Reiseverkehr":{
        "ex":"M.N.DE.W1.S1.S1.T.C.SD._Z._Z._Z.EUR._T._X.N.ALL",
        "im":"M.N.DE.W1.S1.S1.T.D.SD._Z._Z._Z.EUR._T._X.N.ALL",
        },

    "Versicherung_Altersvorsorge":{
        "ex":"M.N.DE.W1.S1.S1.T.C.SF._Z._Z._Z.EUR._T._X.N.ALL",
        "im":"M.N.DE.W1.S1.S1.T.D.SF._Z._Z._Z.EUR._T._X.N.ALL",
        },

    "Finanzsdienstleistungen":{
        "ex":"M.N.DE.W1.S1.S1.T.C.SG._Z._Z._Z.EUR._T._X.N.ALL",
        "im":"M.N.DE.W1.S1.S1.T.D.SG._Z._Z._Z.EUR._T._X.N.ALL",
        },

    "IP_Gebühren":{
        "ex":"M.N.DE.W1.S1.S1.T.C.SH._Z._Z._Z.EUR._T._X.N.ALL",
        "im":"M.N.DE.W1.S1.S1.T.D.SH._Z._Z._Z.EUR._T._X.N.ALL",s
        },

    "Instand_ReparaturDL":{
        "ex":"M.N.DE.W1.S1.S1.T.C.SB._Z._Z._Z.EUR._T._X.N.ALL",
        "im":"M.N.DE.W1.S1.S1.T.D.SB._Z._Z._Z.EUR._T._X.N.ALL",
        },

    "Bauleistungen":{
        "ex":"M.N.DE.W1.S1.S1.T.B.SE1._Z._Z._Z.EUR._T._X.N.ALL",
        "im":"M.N.DE.W1.S1.S1.T.B.SE2._Z._Z._Z.EUR._T._X.N.ALL",
    },

    "IT_EDV":{
        "ex":"M.N.DE.W1.S1.S1.T.C.SI._Z._Z._Z.EUR._T._X.N.ALL",
        "im":"M.N.DE.W1.S1.S1.T.D.SI._Z._Z._Z.EUR._T._X.N.ALL",
    },

    "sonstUnternehmensnaheDL":{
        "ex":"M.N.DE.W1.S1.S1.T.C.SJ._Z._Z._Z.EUR._T._X.N.ALL",
        "im":"M.N.DE.W1.S1.S1.T.D.SJ._Z._Z._Z.EUR._T._X.N.ALL",
    },

    "Kultur_Freizeit":{
        "ex":"M.N.DE.W1.S1.S1.T.C.SK._Z._Z._Z.EUR._T._X.N.ALL",
        "im":"M.N.DE.W1.S1.S1.T.D.SK._Z._Z._Z.EUR._T._X.N.ALL",
    },

    "Regierungsleistungen":{
        "ex":"M.N.DE.W1.S1.S1.T.C.SL._Z._Z._Z.EUR._T._X.N.ALL",
        "im":"M.N.DE.W1.S1.S1.T.D.SL._Z._Z._Z.EUR._T._X.N.ALL",
    },
})

 