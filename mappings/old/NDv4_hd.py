#%%

from data.seriesdataclass import Source, Series, GroupSeries
from data.nowdata import NOWData

#%%

NDv4_hd = NOWData("NDv4_hd")


########################################################################################
# -------------------------------------------------------------------------------------#
# -------------------------------------------------------------------------------------#
# -------------------------------------------------------------------------------------#
# ----------------------------- HARD                 ----------------------------------#
# ----------------------------- INDICATORS           ----------------------------------#
# -------------------------------------------------------------------------------------#
# -------------------------------------------------------------------------------------#
# -------------------------------------------------------------------------------------#
########################################################################################

# -------------------------------------------------------------------------------------#
# --------------- National Accounts ---------------------------------------------------#
# -------------------------------------------------------------------------------------#

NDv4_hd.add(
    Series(
        name="de_gdp_total_ca_cop_sa",
        description="Germany, Gross Domestic Product, Total, Calendar Adjusted (X-13 ARIMA), Constant Prices, SA (X-13 ARIMA), Chained, EUR",
        component="National_Accounts",
        category="GDP",
        transformation="pch",
        source=Source(
            data="mb",
            variable="denaac1000"
        )
    )
)

# -------------------------------------------------------------------------------------#
# --------------- Industrial Production -----------------------------------------------#
# -------------------------------------------------------------------------------------#

NDv4_hd.add(
    GroupSeries(
        series_dict = {
            "de_ip_total_sa": ("deprod1404", "cch"),
            "de_ip_total_ex_constr_sa": ("deprod1370", "cch"),
            "de_ip_total_ex_energy_constr_sa": ("deprod1375", "cch"),
            "de_ip_total_ex_constr_foodbev_sa": ("deprod1398", "cch"),
            "de_ip_total_ex_energy_constr_othertrans_sa": ("deprod3695", "cch"),
            "de_ip_total_ex_energy_constr_energyint_sa": ("deprod3845", "cch"),
            "de_ip_total_ex_energy_constr_energyint_motorveh29_sa": ("deprod3846", "cch"),
            "de_ip_total_ex_energy_constr_motorveh29_sa": ("deprod3847", "cch"),
            "de_ip_total_ex_energy_constr_foodbev_elecgas_sa": ("deprod3690", "cch"),
        },
        source_data="mb",
        component="Hard_Data",
        category="HD_Industrial_Production",
        subcategory="HD_IP_Totals"
    )
)

NDv4_hd.add(
    GroupSeries(
        series_dict = {
            "de_ip_intermed_sa": ("deprod1345", "cch"),
            "de_ip_capital_sa": ("deprod1350", "cch"),
            "de_ip_intermed_capital_sa": ("deprod3710", "cch"),
            "de_ip_consumer_sa": ("deprod1365", "cch"),
            "de_ip_consumer_durable_sa": ("deprod1355", "cch"),
            "de_ip_consumer_nondurable_sa": ("deprod1360", "cch"),
        },
        source_data="mb",
        component="Hard_Data",
        category="HD_Industrial_Production",
        subcategory="HD_IP_Goods_Aggregates"
    )
)

NDv4_hd.add(
    GroupSeries(
        series_dict = {
            "de_ip_capital_ex_motorveh_sa": ("deprod3730", "cch"),
            "de_ip_capital_ex_motorveh_trailers_sa": ("deprod3715", "cch"),
            "de_ip_capital_ex_motorveh_trailers_othertrans_sa": ("deprod3725", "cch"),
            "de_ip_capital_ex_othertrans_sa": ("deprod3720", "cch"),
            "de_ip_capital_ex_airspace_sa": ("deprod3735", "cch"),
            "de_ip_capital_ex_motorveh_airspace_sa": ("deprod3740", "cch"),
            "de_ip_consumer_ex_foodbev_sa": ("deprod3745", "cch"),
        },
        source_data="mb",
        component="Hard_Data",
        category="HD_Industrial_Production",
        subcategory="HD_IP_Goods_Exclusions"
    )
)

NDv4_hd.add(
    GroupSeries(
        series_dict = {
            "de_ip_energy_ex_waterwaste_sa": ("deprod1559", "cch"),
            "de_ip_energy_ex_elecgas_waterwaste_sa": ("deprod3665", "cch"),
            "de_ip_energyint_sa": ("deprod2997", "cch"),
        },
        source_data="mb",
        component="Hard_Data",
        category="HD_Industrial_Production",
        subcategory="HD_IP_Energy"
    )
)

# -------------------------------------------------------------------------------------#
# --------------- Manufacturing -------------------------------------------------------#
# -------------------------------------------------------------------------------------#

NDv4_hd.add(
    Series(
        name="de_ip_manu_total_sa",
        component="Hard_Data",
        category="HD_Manufacturing",
        subcategory="HD_MF_Manufacturing_Sectors",
        transformation="cch",
        source=Source(
            data="mb",
            variable="deprod1414"
        )
    )
)

NDv4_hd.add(
    GroupSeries(
        series_dict = {
            "de_ip_mining_manu_total_sa": ("deprod1997", "cch"),
            "de_ip_manu_other_goods_sa": ("deprod0198", "cch"),
            "de_ip_manu_motorveh_trailers_sa": ("deprod0195", "cch"),
            "de_ip_manu_machinery_nec_sa": ("deprod0194", "cch"),
            "de_ip_manu_leather_sa": ("deprod0181", "cch"),
            "de_ip_manu_glass_ceramic_stone_sa": ("deprod0189", "cch"),
            "de_ip_manu_furniture_sa": ("deprod0197", "cch"),
            "de_ip_manu_food_sa": ("deprod0177", "cch"),
            "de_ip_manu_electrical_equip_sa": ("deprod0193", "cch"),
            "de_ip_manu_elec_optical_sa": ("deprod0192", "cch"),
            "de_ip_manu_clothes_sa": ("deprod0180", "cch"),
            "de_ip_manu_chemicals_sa": ("deprod0186", "cch"),
            "de_ip_manu_beverages_sa": ("deprod0178", "cch"),
            "de_ip_manu_basic_metals_sa": ("deprod0190", "cch"),
            "de_ip_manu_fabricated_metals_sa": ("deprod0191", "cch"),
            "de_ip_manu_other_transport_sa": ("deprod0196", "cch"),
            "de_ip_manu_paper_sa": ("deprod0183", "cch"),
            "de_ip_manu_pharma_sa": ("deprod0187", "cch"),
            "de_ip_manu_printing_sa": ("deprod0184", "cch"),
            "de_ip_manu_repair_install_sa": ("deprod0199", "cch"),
            "de_ip_manu_rubber_plastic_sa": ("deprod0188", "cch"),
            "de_ip_manu_textiles_sa": ("deprod0179", "cch"),
            "de_ip_manu_wood_sa": ("deprod0182", "cch"),
        },
        source_data="mb",
        component="Hard_Data",
        category="HD_Manufacturing",
        subcategory="HD_MF_Manufacturing_Sectors"
    )
)

# -------------------------------------------------------------------------------------#
# --------------- Trade: Total --------------------------------------------------------#
# -------------------------------------------------------------------------------------#

NDv4_hd.add(
    Series(
        name="de_imp_total_destatis_sa",
        component="Hard_Data",
        category="HD_Foreign_Trade",
        subcategory="HD_FT_Imports_Total",
        transformation="cch",
        source=Source(
            data="mb",
            variable="detrad0689"
        )
    )
)

NDv4_hd.add(
    Series(
        name="de_exp_total_destatis_sa",
        component="Hard_Data",
        category="HD_Foreign_Trade",
        subcategory="HD_FT_Exports_Total",
        transformation="cch",
        source=Source(
            data="mb",
            variable="detrad0692"
        )
    )
)

NDv4_hd.add(
    Series(
        name="de_trade_bal_total_destatis_sa",
        component="Hard_Data",
        category="HD_Foreign_Trade",
        subcategory="HD_FT_Balance_Total",
        transformation="cch",
        source=Source(
            data="mb",
            variable="detrad0695"
        )
    )
)

NDv4_hd.add(
    Series(
        name="world_trade_cpb_total_sa",
        component="Hard_Data",
        category="HD_Foreign_Trade",
        subcategory="HD_FT_World_Trade_CPB",
        transformation="cch",
        source=Source(
            data="mb",
            variable="worldtrad0001"
        )
    )
)

# -------------------------------------------------------------------------------------#
# --------------- Turnover ------------------------------------------------------------#
# -------------------------------------------------------------------------------------#


NDv4_hd.add(
    GroupSeries(
        series_dict = {
            "de_to_mfg_dom_idx": ("detrad3415", "cch"),
            "de_to_capital_dom_idx": ("detrad1904", "cch"),
            "de_to_intermed_dom_idx": ("detrad1879", "cch"),
            "de_to_cons_dom_idx": ("detrad1929", "cch"),
            "de_to_dur_dom_idx": ("detrad1954", "cch"),
            "de_to_nondur_dom_idx": ("detrad1979", "cch"),
            "de_to_energy_dom_idx": ("detrad3365", "cch"),
        },
        source_data="mb",
        component="Hard_Data",
        category="HD_Manufacturing_Turnover",
        subcategory="HD_TO_Domestic"
    )
)

NDv4_hd.add(
    GroupSeries(
        series_dict = {
            "de_to_mfg_ea_idx": ("detrad3417", "cch"),
            "de_to_capital_ea_idx": ("detrad1906", "cch"),
            "de_to_intermed_ea_idx": ("detrad1881", "cch"),
            "de_to_cons_ea_idx": ("detrad1931", "cch"),
            "de_to_dur_ea_idx": ("detrad1956", "cch"),
            "de_to_nondur_ea_idx": ("detrad1981", "cch"),
            "de_to_energy_ea_idx": ("detrad3367", "cch"),
        },
        source_data="mb",
        component="Hard_Data",
        category="HD_Manufacturing_Turnover",
        subcategory="HD_TO_EuroArea"
    )
)

NDv4_hd.add(
    GroupSeries(
        series_dict = {
            "de_to_mfg_for_idx": ("detrad3416", "cch"),
            "de_to_capital_for_idx": ("detrad1905", "cch"),
            "de_to_intermed_for_idx": ("detrad1880", "cch"),
            "de_to_cons_for_idx": ("detrad1930", "cch"),
            "de_to_dur_for_idx": ("detrad1955", "cch"),
            "de_to_nondur_for_idx": ("detrad1980", "cch"),
            "de_to_energy_for_idx": ("detrad3366", "cch"),
        },
        source_data="mb",
        component="Hard_Data",
        category="HD_Manufacturing_Turnover",
        subcategory="HD_TO_Foreign"
    )
)

NDv4_hd.add(
    GroupSeries(
        series_dict = {
            "de_to_mfg_nonea_idx": ("detrad3418", "cch"),
            "de_to_capital_nonea_idx": ("detrad1907", "cch"),
            "de_to_intermed_nonea_idx": ("detrad1882", "cch"),
            "de_to_cons_nonea_idx": ("detrad1932", "cch"),
            "de_to_dur_nonea_idx": ("detrad1957", "cch"),
            "de_to_nondur_nonea_idx": ("detrad1982", "cch"),
            "de_to_energy_nonea_idx": ("detrad3368", "cch"),
        },
        source_data="mb",
        component="Hard_Data",
        category="HD_Manufacturing_Turnover",
        subcategory="HD_TO_NonEuroArea"
    )
)

NDv4_hd.add(
    GroupSeries(
        series_dict = {
            "de_to_mfg_total_idx": ("detrad3414", "cch"),
            "de_to_capital_total_idx": ("detrad1903", "cch"),
            "de_to_intermed_total_idx": ("detrad1878", "cch"),
            "de_to_dur_total_idx": ("detrad1953", "cch"),
            "de_to_nondur_total_idx": ("detrad1978", "cch"),
            "de_to_cons_total_idx": ("detrad1928", "cch"),
            "de_to_energy_total_idx": ("detrad3364", "cch"),
        },
        source_data="mb",
        component="Hard_Data",
        category="HD_Manufacturing_Turnover",
        subcategory="HD_TO_Total"
    )
)

# -------------------------------------------------------------------------------------#
# --------------- New Orders ----------------------------------------------------------#
# -------------------------------------------------------------------------------------#

# --------------- Manufacturing -------------------------------------------------------#

NDv4_hd.add(
    GroupSeries(
        series_dict = {
            "de_no_mfg_total_idx": ("detrad0689", "cch"),
            "de_no_mfg_dom_total_idx": ("deprod2113", "cch"),
        },
        source_data="mb",
        component="Hard_Data",
        category="HD_New_Orders",
        subcategory="HD_NO_Manufacturing"
    )
)

# --------------- By Goods -----------------------------------------------------------#

NDv4_hd.add(
    GroupSeries(
        series_dict = {
            "de_no_mfg_capital_idx":    ("deprod2124", "cch"),
            "de_no_mfg_intermed_idx":   ("deprod2119", "cch"),
            "de_no_mfg_cons_idx":       ("deprod2129", "cch"),
            "de_no_mfg_durable_idx":    ("deprod2134", "cch"),
            "de_no_mfg_nondurable_idx": ("deprod2139", "cch"),
        },
        source_data="mb",
        component="Hard_Data",
        category="HD_New_Orders",
        subcategory="HD_NO_ByGoods"
    )
)

# --------------- Construction ------------------------------------------------------#

NDv4_hd.add(
    GroupSeries(
        series_dict = {
            "de_cstr_no_total_sa": ("deprod1633", "cch"),  
            "de_cstr_no_build_total_sa":  ("deprod1635", "cch"),
            "de_cstr_no_civil_total_sa":  ("deprod1643", "cch"),
        },
        source_data="mb",
        component="Hard_Data",
        category="HD_Construction",
        subcategory="HD_CSTR_Totals"
    )
)

NDv4_hd.add(
    GroupSeries(
        series_dict = {
            "de_cstr_no_build_house_sa":     ("deprod1637", "cch"),
            "de_cstr_no_build_ex_house_sa":  ("deprod1639", "cch"),
        },
        source_data="mb",
        component="Hard_Data",
        category="HD_Construction",
        subcategory="HD_CSTR_Building"
    )
)

NDv4_hd.add(
    GroupSeries(
        series_dict = {
            "de_cstr_no_road_build_sa":    ("deprod1645", "cch"),
            "de_cstr_no_civil_ex_road_sa": ("deprod1647", "cch"),
        },
        source_data="mb",
        component="Hard_Data",
        category="HD_Construction",
        subcategory="HD_CSTR_Civil"
    )
)


# -------------------------------------------------------------------------------------#
# --------------- Trade: Imports ------------------------------------------------------#
# -------------------------------------------------------------------------------------#

NDv4_hd.add(
    GroupSeries(
        series_dict = {
            "de_imp_europe_destatis_sa": ("detrad0711", "cch"),
            "de_imp_eu27exuk_destatis_sa": ("detrad0712", "cch"),
            "de_imp_ea18_destatis_sa": ("detrad0713", "cch"),
            "de_imp_other_eur_destatis_sa": ("detrad0714", "cch"),

            "de_imp_noneur_destatis_sa": ("detrad0715", "cch"),
            "de_imp_us_destatis_sa": ("detrad0716", "cch"),
            "de_imp_asia_destatis_sa": ("detrad0717", "cch"),
            "de_imp_opec_destatis_sa": ("detrad0718", "cch"),
        },
        source_data="mb",
        component="Hard_Data",
        category="HD_Foreign_Trade",
        subcategory="HD_FT_Imports_ByRegion"
    )
)

# -------------------------------------------------------------------------------------#
# --------------- Trade: Exports ------------------------------------------------------#
# -------------------------------------------------------------------------------------#

# Regions / blocs
NDv4_hd.add(
    GroupSeries(
        series_dict = {
            "de_exp_eu27exuk_destatis_sa": ("detrad00001", "cch"),
            "de_exp_ea_destatis_sa": ("detrad00002", "cch"),
            "de_exp_nonea_destatis_sa": ("detrad00021", "cch"),
            "de_exp_non_eu_destatis_sa": ("detrad00030", "cch"),
            "de_exp_uk_destatis_sa": ("detrad00031", "cch"),
        },
        source_data="mb",
        component="Hard_Data",
        category="HD_Foreign_Trade",
        subcategory="HD_FT_Exports_ByRegion"
    )
)

# Countries
NDv4_hd.add(
    GroupSeries(
        series_dict = {
            "de_exp_us_destatis_sa": ("detrad00039", "cch"),
            "de_exp_china_destatis_sa": ("detrad00040", "cch"),
            "de_exp_japan_destatis_sa": ("detrad00042", "cch"),
            "de_exp_india_destatis_sa": ("detrad00041", "cch"),
            "de_exp_switzerland_destatis_sa": ("detrad00034", "cch"),
            "de_exp_poland_destatis_sa": ("detrad00025", "cch"),
            "de_exp_france_destatis_sa": ("detrad00006", "cch"),
            "de_exp_netherlands_destatis_sa": ("detrad00014", "cch"),
            "de_exp_mexico_destatis_sa": ("detrad00038", "cch"),
            "de_exp_australia_destatis_sa": ("detrad00044", "cch"),
            "de_exp_turkey_destatis_sa": ("detrad00035", "cch"),
            "de_exp_south_korea_destatis_sa": ("detrad00043", "cch"),
            "de_exp_russia_destatis_sa": ("detrad00033", "cch"),
            "de_exp_norway_destatis_sa": ("detrad00032", "cch"),
            "de_exp_slovakia_destatis_sa": ("detrad00017", "cch"),
            "de_exp_hungary_destatis_sa": ("detrad00029", "cch"),
            "de_exp_brazil_destatis_sa": ("detrad00037", "cch"),
            "de_exp_czech_republic_destatis_sa": ("detrad00028", "cch"),
            "de_exp_italy_destatis_sa": ("detrad00009", "cch"),
            "de_exp_south_africa_destatis_sa": ("detrad00036", "cch"),
            "de_exp_ireland_destatis_sa": ("detrad00008", "cch"),
            "de_exp_romania_destatis_sa": ("detrad00026", "cch"),
            "de_exp_austria_destatis_sa": ("detrad00015", "cch"),
            "de_exp_denmark_destatis_sa": ("detrad00023", "cch"),
            "de_exp_spain_destatis_sa": ("detrad00019", "cch"),
            "de_exp_slovenia_destatis_sa": ("detrad00018", "cch"),
            "de_exp_belgium_destatis_sa": ("detrad00003", "cch"),
            "de_exp_sweden_destatis_sa": ("detrad00027", "cch"),
            "de_exp_cyprus_destatis_sa": ("detrad00020", "cch"),
            "de_exp_lithuania_destatis_sa": ("detrad00011", "cch"),
            "de_exp_greece_destatis_sa": ("detrad00007", "cch"),
            "de_exp_latvia_destatis_sa": ("detrad00010", "cch"),
            "de_exp_portugal_destatis_sa": ("detrad00016", "cch"),
            "de_exp_croatia_destatis_sa": ("detrad00024", "cch"),
            "de_exp_finland_destatis_sa": ("detrad00005", "cch"),
            "de_exp_estonia_destatis_sa": ("detrad00004", "cch"),
            "de_exp_bulgaria_destatis_sa": ("detrad00022", "cch"),
            "de_exp_malta_destatis_sa": ("detrad00013", "cch"),
            "de_exp_luxembourg_destatis_sa": ("detrad00012", "cch"),
        },
        source_data="mb",
        component="Hard_Data",
        category="HD_Foreign_Trade",
        subcategory="HD_FT_Exports_ByCountry"
    )
)

# -------------------------------------------------------------------------------------#
# --------------- Trade: Consumption related ------------------------------------------#
# -------------------------------------------------------------------------------------#

NDv4_hd.add(
    Series(
        name="de_dt_cons_turn_sa",
        component="Hard_Data",
        category="HD_Domestic_Trade",
        subcategory="HD_DT_Consumption_Turnover",
        transformation="cch",
        source=Source(
            data="mb",
            variable="detrad8161"
        )
    )
)

NDv4_hd.add(
    Series(
        name="de_dt_cons_turn_sa",
        component="Hard_Data",
        category="HD_Domestic_Trade",
        subcategory="HD_DT_Vehicles_Turnover",
        transformation="cch",
        source=Source(
            data="mb",
            variable="detrad1704"
        )
    )
)

NDv4_hd.add(
    Series(
        name="de_dt_whs_turn_sa",
        component="Hard_Data",
        category="HD_Domestic_Trade",
        subcategory="HD_DT_Wholesale_Turnover",
        transformation="cch",
        source=Source(
            data="mb",
            variable="detrad8150"
        )
    )
)

NDv4_hd.add(
    GroupSeries(
        series_dict = {
            "de_dt_rt_ex_veh_turn_sa": ("detrad1360", "cch"),
            "de_dt_rt_incl_veh_turn_sa": ("detrad0002", "cch"),
            "de_dt_rt_ex_veh_fill_turn_sa": ("detrad8244", "cch"),
        },
        source_data="mb",
        component="Hard_Data",
        category="HD_Domestic_Trade",
        subcategory="HD_DT_Retail_Turnover"
    )
)

NDv4_hd.add(
    GroupSeries(
        series_dict = {
            "de_dt_serv_accom_food_turn_sa": ("detrad3877", "cch"),
            "de_dt_serv_accommodation_turn_sa": ("detrad3841", "cch"),
            "de_dt_serv_food_bev_turn_sa": ("detrad3857", "cch"),
            "de_dt_serv_accom_total_turn_sa": ("detrad8954", "cch"),
            "de_dt_serv_selected_accom_food_turn_sa": ("detrad8931", "cch"),
            "de_dt_serv_selected_total_turn_sa": ("detrad8932", "cch"),
            "de_dt_serv_selected_business_turn_sa": ("detrad8933", "cch"),
            "de_dt_serv_transport_storage_turn_sa": ("detrad8934", "cch"),
            "de_dt_serv_info_comm_turn_sa": ("detrad8955", "cch"),
            "de_dt_serv_prof_tech_turn_sa": ("detrad8980", "cch"),
            "de_dt_serv_admin_support_turn_sa": ("detrad8997", "cch"),
            "de_dt_serv_real_estate_turn_sa": ("detrad8975", "cch"),
            "de_dt_serv_real_estate_cp_turn_sa": ("detrad8588", "cch"),
        },
        source_data="mb",
        component="Hard_Data",
        category="HD_Domestic_Trade",
        subcategory="HD_DT_Services_Turnover"   
    )
)


# -------------------------------------------------------------------------------------#
# --------------- Labor Market --------------------------------------------------------#
# -------------------------------------------------------------------------------------#

NDv4_hd.add(
    GroupSeries(
        series_dict = {
            "de_unemp_total_sa": ("delama0817", "pch"),
            "de_unemp_rate_sa": ("delama0822", "pch"),
            "de_unemp_ilo_trend": ("delama1321", "pch"),
            "de_unemp_rate_ilo_trend": ("delama1322", "pch"),
            "de_unemp_germans_total": ("delama1040", "pch"),
            "de_unemp_foreigners_total": ("delama1049", "pch"),
        },
        source_data="mb",
        component="Hard_Data",
        category="HD_Labor_Market",
        subcategory="HD_LM_Unemployment"
    )
)

NDv4_hd.add(
    GroupSeries(
        series_dict = {
            "de_emp_total_domestic_sa": ("delama1317", "pch"),
            "de_emp_total_resident_sa": ("delama1314", "pch"),
            "de_emp_ilo_trend": ("delama1320", "pch"),
        },
        source_data="mb",
        component="Hard_Data",
        category="HD_Labor_Market",
        subcategory="HD_LM_Employment"
    )
)

NDv4_hd.add(
    GroupSeries(
        series_dict = {
            "de_lowpaid_parttime_sa": ("buba_mb_66280", "pch"),
            "de_lowpaid_parttime_nsa": ("buba_mb_66290", "pch"),
        },
        source_data="mb",
        component="Hard_Data",
        category="HD_Labor_Market",
        subcategory="HD_LM_LowPaid_PartTime"
    )
)
