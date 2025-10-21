#%%

from data.seriesdataclass import Source, Series, GroupSeries
from data.nowdata import NOWData

#%%

NDv5 = NOWData("NDv5")


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

NDv5.add(
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

NDv5.add(
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

NDv5.add(
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

NDv5.add(
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

NDv5.add(
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

NDv5.add(
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

NDv5.add(
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

NDv5.add(
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

NDv5.add(
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

NDv5.add(
    Series(
        name="de_trade_bal_total_destatis_sa",
        component="Hard_Data",
        category="HD_Foreign_Trade",
        subcategory="HD_FT_Balance_Total",
        transformation="chg",
        source=Source(
            data="mb",
            variable="detrad0695"
        )
    )
)

NDv5.add(
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


NDv5.add(
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

NDv5.add(
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

NDv5.add(
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

NDv5.add(
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

NDv5.add(
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

NDv5.add(
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

NDv5.add(
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

NDv5.add(
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

NDv5.add(
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

NDv5.add(
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

NDv5.add(
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
NDv5.add(
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
NDv5.add(
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

NDv5.add(
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

NDv5.add(
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

NDv5.add(
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

NDv5.add(
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

NDv5.add(
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

NDv5.add(
    GroupSeries(
        series_dict = {
            "de_unemp_total_sa": ("delama0817", "cch"),
            "de_unemp_rate_sa": ("delama0822", "pch"),
            "de_unemp_ilo_trend": ("delama1321", "cch"),
            "de_unemp_rate_ilo_trend": ("delama1322", "pch"),
            "de_unemp_germans_total": ("delama1040", "cch"),
            "de_unemp_foreigners_total": ("delama1049", "cch"),
        },
        source_data="mb",
        component="Hard_Data",
        category="HD_Labor_Market",
        subcategory="HD_LM_Unemployment"
    )
)

NDv5.add(
    GroupSeries(
        series_dict = {
            "de_emp_total_domestic_sa": ("delama1317", "cch"),
            "de_emp_total_resident_sa": ("delama1314", "cch"),
            "de_emp_ilo_trend": ("delama1320", "cch"),
        },
        source_data="mb",
        component="Hard_Data",
        category="HD_Labor_Market",
        subcategory="HD_LM_Employment"
    )
)

NDv5.add(
    GroupSeries(
        series_dict = {
            "de_lowpaid_parttime_sa": ("buba_mb_66280", "cch"),
            "de_lowpaid_parttime_nsa": ("buba_mb_66290", "cch"),
        },
        source_data="mb",
        component="Hard_Data",
        category="HD_Labor_Market",
        subcategory="HD_LM_LowPaid_PartTime"
    )
)

########################################################################################
# -------------------------------------------------------------------------------------#
# -------------------------------------------------------------------------------------#
# -------------------------------------------------------------------------------------#
# ----------------------------- SOFT                 ----------------------------------#
# ----------------------------- INDICATORS           ----------------------------------#
# -------------------------------------------------------------------------------------#
# -------------------------------------------------------------------------------------#
# -------------------------------------------------------------------------------------#
########################################################################################

# -------------------------------------------------------------------------------------#
# --------------- Ifo -----------------------------------------------------------------#
# -------------------------------------------------------------------------------------#
NDv5.add(
    GroupSeries(
        series_dict = {
            "de_ifo_bs_total_expect_6m_bal_sa": ("desurv01051", "chg"),
            "de_ifo_bs_total_situation_bal_sa": ("desurv01050", "chg"),
            "de_ifo_bs_total_climate_avg_sa": ("desurv01049", "chg"),
        },
        source_data="mb",
        component="Soft_Data",
        category="SD_Business_Surveys",
        subcategory="SD_BS_Ifo_Headchge"
    )
)

NDv5.add(
    GroupSeries(
        series_dict = {
            "de_ifo_bs_manu_expect_6m_bal_sa": ("desurv1146", "chg"),
            "de_ifo_bs_manu_climate_avg_sa": ("desurv0022", "chg"),
            "de_ifo_bs_manu_situation_bal_sa": ("desurv1124", "chg"),
            "de_ifo_bs_manu_export_expect_3m_bal_sa": ("desurv1142", "chg"),
        },
        source_data="mb",
        component="Soft_Data",
        category="SD_Business_Surveys",
        subcategory="SD_BS_Ifo_Manufacturing"
    )
)

NDv5.add(
    GroupSeries(
        series_dict = {
            "de_ifo_bs_services_expect_6m_bal_sa": ("desurv0343", "chg"),
            "de_ifo_bs_services_climate_avg_sa": ("desurv0341", "chg"),
            "de_ifo_bs_services_situation_bal_sa": ("desurv0342", "chg"),
        },
        source_data="mb",
        component="Soft_Data",
        category="SD_Business_Surveys",
        subcategory="SD_BS_Ifo_Services"
    )
)

NDv5.add(
    GroupSeries(
        series_dict = {
            "de_ifo_bs_constr_climate_avg_sa": ("desurv0023", "chg"),
            "de_ifo_bs_constr_expect_6m_bal_sa": ("desurv1032", "chg"),
            "de_ifo_bs_constr_situation_bal_sa": ("desurv1028", "chg"),
        },
        source_data="mb",
        component="Soft_Data",
        category="SD_Business_Surveys",
        subcategory="SD_BS_Ifo_Construction"
    )
)

NDv5.add(
    GroupSeries(
        series_dict = {
            "de_ifo_bs_trade_climate_avg_sa": ("deifo_ghanges0_kld_bds", "chg"),
            "de_ifo_bs_trade_situation_bal_sa": ("deifo_ghanges0_gus_bds", "chg"),
            "de_ifo_bs_trade_expect_6m_bal_sa": ("deifo_ghanges0_ges_bds", "chg"),
        },
        source_data="mb",
        component="Soft_Data",
        category="SD_Business_Surveys",
        subcategory="SD_BS_Ifo_Trade"
    )
)

NDv5.add(
    GroupSeries(
        series_dict = {
            "de_ifo_bs_tradeindustry_expect_6m_bal_sa": ("desurv0006", "chg"),
            "de_ifo_bs_tradeindustry_climate_avg_sa": ("desurv0004", "chg"),
            "de_ifo_bs_tradeindustry_situation_bal_sa": ("desurv0005", "chg"),
        },
        source_data="mb",
        component="Soft_Data",
        category="SD_Business_Surveys",
        subcategory="SD_BS_Ifo_Trade_Industry"
    )
)

NDv5.add(
    GroupSeries(
        series_dict = {
            "de_ifo_bs_manu_cons_climate_avg_sa": ("desurv1261", "chg"),
            "de_ifo_bs_manu_cons_expect_6m_bal_sa": ("desurv1257", "chg"),
            "de_ifo_bs_manu_cons_situation_bal_sa": ("desurv1235", "chg"),
        },
        source_data="mb",
        component="Soft_Data",
        category="SD_Business_Surveys",
        subcategory="SD_BS_Ifo_Manufacturing_ConsumerGoods"
    )
)

NDv5.add(
    GroupSeries(
        series_dict = {
            "de_ifo_bs_manu_ex_foodbev_climate_avg_sa": ("desurv1177", "chg"),
            "de_ifo_bs_manu_ex_foodbev_expect_6m_bal_sa": ("desurv1173", "chg"),
            "de_ifo_bs_manu_ex_foodbev_situation_bal_sa": ("desurv1151", "chg"),
        },
        source_data="mb",
        component="Soft_Data",
        category="SD_Business_Surveys",
        subcategory="SD_BS_Ifo_Manufacturing_ExFoodBevTob"
    )
)

NDv5.add(
    GroupSeries(
        series_dict = {
            "de_ifo_bs_trade_emp_expect_bal_sa": ("deifo_ghanges0_bes_bds", "chg"),
            "de_ifo_bs_manu_emp_expect_3m_bal_sa": ("desurv1148", "chg"),
            "de_ifo_bs_services_emp_expect_bal_sa": ("desurv8719", "chg"),
            "de_ifo_bs_constr_emp_expect_3_4m_bal_sa": ("desurv7681", "chg"),
        },
        source_data="mb",
        component="Soft_Data",
        category="SD_Business_Surveys",
        subcategory="SD_BS_Ifo_Employment"
    )
)

NDv5.add(
    GroupSeries(
        series_dict = {
            "de_ifo_bs_east_manu_climate_avg_sa": ("desurv6749", "chg"),
            "de_ifo_bs_east_manu_expect_6m_bal_sa": ("desurv6745", "chg"),
            "de_ifo_bs_east_manu_situation_bal_sa": ("desurv6723", "chg"),
        },
        source_data="mb",
        component="Soft_Data",
        category="SD_Business_Surveys",
        subcategory="SD_BS_Ifo_East_Manufacturing"
    )
)

NDv5.add(
    GroupSeries(
        series_dict = {
            "de_ifo_bs_east_constr_climate_avg_sa": ("desurv1088", "chg"),
            "de_ifo_bs_east_constr_expect_6m_bal_sa": ("desurv1096", "chg"),
            "de_ifo_bs_east_constr_situation_bal_sa": ("desurv1092", "chg"),
        },
        source_data="mb",
        component="Soft_Data",
        category="SD_Business_Surveys",
        subcategory="SD_BS_Ifo_East_Construction"
    )
)

NDv5.add(
    GroupSeries(
        series_dict = {
            "de_ifo_bs_east_tradeindustry_climate_avg_sa": ("desurv1058", "chg"),
            "de_ifo_bs_east_tradeindustry_expect_6m_bal_sa": ("desurv1066", "chg"),
            "de_ifo_bs_east_tradeindustry_situation_bal_sa": ("desurv1062", "chg"),
        },
        source_data="mb",
        component="Soft_Data",
        category="SD_Business_Surveys",
        subcategory="SD_BS_Ifo_East_Trade_Industry"
    )
)

NDv5.add(
    GroupSeries(
        series_dict = {
            "de_ifo_bs_east_manu_ex_foodbev_climate_avg_sa": ("desurv6777", "chg"),
            "de_ifo_bs_east_manu_ex_foodbev_expect_6m_bal_sa": ("desurv6773", "chg"),
            "de_ifo_bs_east_manu_ex_foodbev_situation_bal_sa": ("desurv6751", "chg"),
        },
        source_data="mb",
        component="Soft_Data",
        category="SD_Business_Surveys",
        subcategory="SD_BS_Ifo_East_Manufacturing_ExFoodBevTob"
    )
)

NDv5.add(
    GroupSeries(
        series_dict = {
            "de_ifo_bs_east_manu_cons_climate_avg_sa": ("desurv6861", "chg"),
            "de_ifo_bs_east_manu_cons_expect_6m_bal_sa": ("desurv6857", "chg"),
            "de_ifo_bs_east_manu_cons_situation_bal_sa": ("desurv6835", "chg"),
        },
        source_data="mb",
        component="Soft_Data",
        category="SD_Business_Surveys",
        subcategory="SD_BS_Ifo_East_Manufacturing_ConsumerGoods"
    )
)

NDv5.add(
    GroupSeries(
        series_dict = {
            "de_ifo_bs_manu_cons_prices_expect_3m_bal_sa": ("desurv1251", "chg"),
            "de_ifo_bs_manu_dur_cons_prices_expect_3m_bal_sa": ("desurv1279", "chg"),
            "de_ifo_bs_manu_electrical_equip_prices_expect_3m_bal_sa": ("desurv4975", "chg"),
            "de_ifo_bs_manu_nondur_cons_prices_expect_3m_bal_sa": ("desurv1307", "chg"),
        },
        source_data="mb",
        component="Soft_Data",
        category="SD_Business_Surveys",
        subcategory="SD_BS_Ifo_Price_Expectations"
    )
)

NDv5.add(
    GroupSeries(
        series_dict = {
            "de_ifo_caputil_constr_total_sa": ("deprod2431", "chg"),
            "de_ifo_caputil_constr_building_avg_sa": ("deprod2435", "chg"),
            "de_ifo_caputil_constr_civil_avg_sa": ("deprod2433", "chg"),
        },
        source_data="mb",
        component="Soft_Data",
        category="SD_Business_Surveys",
        subcategory="SD_BS_Ifo_Capacity_Utilization"
    )
)

NDv5.add(
    GroupSeries(
        series_dict = {
            "de_ifo_export_climate_sa": ("desurv0344", "chg"),
            # "de_ifo_import_climate_sa": ("desurv0046", "chg"),
        },
        source_data="mb",
        component="Soft_Data",
        category="SD_Business_Surveys",
        subcategory="SD_BS_Ifo_Trade_Climate"
    )
)


NDv5.add(
    GroupSeries(
        series_dict = {
            "de_ifo_bs_constr_res_orders": ("deifo_f4010300_bvsa_bdu", "chg"),
            "de_ifo_bs_manu_orders": ("deifo_c0000000_bvsa_bdu", "chg"),
            "de_ifo_bs_constr_road_orders": ("deifo_f4020100_bvsa_bdu", "chg"),
        },
        source_data="mb",
        component="Soft_Data",
        category="SD_Business_Surveys",
        subcategory="SD_BS_Ifo_Orders"
    )
)

NDv5.add(
    GroupSeries(
        series_dict = {
            "de_ifo_bs_manu_expect_6m_idx_sa": ("desurv1011", "chg"),
            "de_ifo_bs_constr_expect_6m_idx_sa": ("desurv1034", "chg"),
            "de_ifo_bs_retail_incl_veh_expect_6m_idx_sa": ("desurv1056", "chg"),
            "de_ifo_bs_whs_incl_veh_expect_6m_idx_sa": ("desurv1045", "chg"),
        },
        source_data="mb",
        component="Soft_Data",
        category="SD_Business_Surveys",
        subcategory="SD_BS_Ifo_Sector_Expectations"
    )
)

NDv5.add(
    GroupSeries(
        series_dict = {
            "de_ifo_emp_barometer_sa": ("desurv0340", "chg"),
        },
        source_data="mb",
        component="Soft_Data",
        category="SD_Business_Surveys",
        subcategory="SD_BS_Ifo_Employment"
    )
)

# -------------------------------------------------------------------------------------#
# --------------- GfK -----------------------------------------------------------------#
# -------------------------------------------------------------------------------------#

NDv5.add(
    GroupSeries(
        series_dict = {
            "de_gfk_cc_income_expect": ("desurv0027", "chg"),
            "de_gfk_cc_econ_expect": ("desurv0026", "chg"),
            "de_gfk_cc_wilchgg_buy": ("desurv0028", "chg"),
            "de_gfk_cc_indicator": ("desurv0029", "chg"),
        },
        source_data="mb",
        component="Soft_Data",
        category="SD_Consumer_Surveys",
        subcategory="SD_CS_GfK_Consumer_Climate"
    )
)

# -------------------------------------------------------------------------------------#
# --------------- ZEW Financial Market Report -----------------------------------------#
# -------------------------------------------------------------------------------------#

NDv5.add(
    GroupSeries(
        series_dict = {
            "de_zew_econ_expect_bal": ("desurv0017", "chg"),
            "de_zew_current_bal": ("desurv0018", "chg"),
            "de_zew_infl_rate_bal": ("desurv0050", "chg"),
            "de_zew_auto_bal": ("desurv0068", "chg"),
            "de_zew_mecheng_bal": ("desurv0072", "chg"),
            "de_zew_steel_bal": ("desurv0070", "chg"),
            "de_zew_services_bal": ("desurv0076", "chg"),
            "de_zew_retail_cons_bal": ("desurv0073", "chg"),
            "de_zew_chem_pharma_bal": ("desurv0069", "chg"),
            "de_zew_electronics_bal": ("desurv0071", "chg"),
            "de_zew_construction_bal": ("desurv0074", "chg"),
            "de_zew_banks_bal": ("desurv0066", "chg"),
            "de_zew_telecom_bal": ("desurv0077", "chg"),
            "de_zew_insurance_bal": ("desurv0067", "chg"),
            "de_zew_utilities_bal": ("desurv0075", "chg"),
            "de_zew_it_bal": ("desurv0078", "chg"),
            "de_zew_dax_bal": ("desurv0054", "chg"),
            "de_zew_lt_rates_bal": ("desurv0052", "chg"),
        },
        source_data="mb",
        component="Soft_Data",
        category="SD_Economic_Surveys",
        subcategory="SD_ES_ZEW_Financial_Market_Report"
    )
)

# -------------------------------------------------------------------------------------#
# --------------- DG ECFIN ------------------------------------------------------------#
# -------------------------------------------------------------------------------------#


NDv5.add(
    GroupSeries(
        series_dict = {
            "de_ecfin_cons_unemp_expect_12m_bal_sa": ("cons2_de_tot_7_bs_m", "lin"),
        },
        source_data="mb",
        component="Soft_Data",
        category="SD_Consumer_Surveys",
        subcategory="SD_CS_ECFIN_Expectations"
    )
)

# -------------------------------------------------------------------------------------#
# --------------- Policy Uncertainty --------------------------------------------------#
# -------------------------------------------------------------------------------------#


NDv5.add(
    GroupSeries(
        series_dict = {
            "de_epu_news_idx": ("deepunnewsindex", "chg"),
        },
        source_data="mb",
        component="Soft_Data",
        category="SD_Uncertainty_Indices",
        subcategory="SD_Uncertainty_Indices"
    )
)

########################################################################################
# -------------------------------------------------------------------------------------#
# -------------------------------------------------------------------------------------#
# -------------------------------------------------------------------------------------#
# ----------------------------- PRICES               ----------------------------------#
# ----------------------------- DATA                 ----------------------------------#
# -------------------------------------------------------------------------------------#
# -------------------------------------------------------------------------------------#
# -------------------------------------------------------------------------------------#
########################################################################################


# -------------------------------------------------------------------------------------#
# --------------- Prices --------------------------------------------------------------#
# -------------------------------------------------------------------------------------#

NDv5.add(
    GroupSeries(
        series_dict = {
            "de_cpi_total_idx": ("depric0001", "cch"),
            "de_cpi_core_idx": ("depric2458", "cch"),
            "de_cpi_goods_idx": ("depric2453", "cch"),
            "de_cpi_services_idx": ("depric2457", "cch"),
        },
        source_data="mb",
        component="Prices_Monetary",
        category="PM_Consumer_Prices",
        subcategory="PM_CPI_Totals"
    )
)

NDv5.add(
    GroupSeries(
        series_dict = {
            "de_cpi_food_nonalc_idx": ("depric0671", "cch"),
            "de_cpi_housing_utilities_idx": ("depric0674", "cch"),
            "de_cpi_health_idx": ("depric0676", "cch"),
            "de_cpi_clothing_footwear_idx": ("depric0673", "cch"),
            "de_cpi_transport_idx": ("depric0677", "cch"),
            "de_cpi_rest_hotels_idx": ("depric0681", "cch"),
            "de_cpi_furn_household_idx": ("depric0675", "cch"),
            "de_cpi_misc_goods_services_idx": ("depric0682", "cch"),
            "de_cpi_communication_idx": ("depric0678", "cch"),
            "de_cpi_education_idx": ("depric0680", "cch"),
            "de_cpi_alc_tob_idx": ("depric0672", "cch"),
            "de_cpi_recreation_culture_idx": ("depric0679", "cch"),
        },
        source_data="mb",
        component="Prices_Monetary",
        category="PM_Consumer_Prices",
        subcategory="PM_CPI_Sectors"
    )
)

# --------------- Export Prices -------------------------------------------------------#

NDv5.add(
    GroupSeries(
        series_dict = {
            "de_xpi_total_idx": ("depric4691", "cch"),
            "de_xpi_ex_energy_idx": ("depric4965", "cch"),
            "de_xpi_ea_idx": ("depric4970", "cch"),
            "de_xpi_non_ea_idx": ("depric4971", "cch"),
        },
        source_data="mb",
        component="Prices_Monetary",
        category="PM_Export_Prices",
        subcategory="PM_XPI_Totals"
    )
)

NDv5.add(
    GroupSeries(
        series_dict = {
            "de_xpi_cons_goods_idx": ("depric4962", "cch"),
            "de_xpi_dur_cons_goods_idx": ("depric4963", "cch"),
            "de_xpi_non_dur_cons_goods_idx": ("depric4964", "cch"),
            "de_xpi_invest_goods_idx": ("depric4961", "cch"),
            "de_xpi_intermed_goods_idx": ("depric4960", "cch"),
            "de_xpi_energy_idx": ("depric4959", "cch"),
        },
        source_data="mb",
        component="Prices_Monetary",
        category="PM_Export_Prices",
        subcategory="PM_XPI_Goods_Categories"
    )
)

NDv5.add(
    GroupSeries(
        series_dict = {
            "de_xpi_ind_machines_idx": ("depric4748", "cch"),
            "de_xpi_ind_cars_parts_idx": ("depric4749", "cch"),
            "de_xpi_ind_electrical_mach_appar_idx": ("depric4747", "cch"),
            "de_xpi_ind_data_elec_optical_idx": ("depric4746", "cch"),
            "de_xpi_ind_chemicals_idx": ("depric4740", "cch"),
            "de_xpi_ind_pharma_idx": ("depric4741", "cch"),
            "de_xpi_ind_rubber_plastic_idx": ("depric4742", "cch"),
            "de_xpi_ind_metal_products_idx": ("depric4745", "cch"),
            "de_xpi_ind_metals_idx": ("depric4744", "cch"),
            "de_xpi_ind_glass_ceramics_stone_idx": ("depric4743", "cch"),
            "de_xpi_ind_paper_idx": ("depric4738", "cch"),
            "de_xpi_ind_wood_products_idx": ("depric4737", "cch"),
            "de_xpi_ind_textiles_idx": ("depric4734", "cch"),
            "de_xpi_ind_clothing_idx": ("depric4735", "cch"),
            "de_xpi_ind_furniture_idx": ("depric4751", "cch"),
            "de_xpi_ind_beverages_idx": ("depric4732", "cch"),
            "de_xpi_ind_food_feed_idx": ("depric4731", "cch"),
            "de_xpi_ind_tobacco_idx": ("depric4733", "cch"),
            "de_xpi_ind_goods_nec_idx": ("depric4941", "cch"),
            "de_xpi_ind_oil_gas_idx": ("depric4728", "cch"),
            "de_xpi_ind_coal_idx": ("depric4727", "cch"),
            "de_xpi_ind_cokery_mineral_oil_idx": ("depric4739", "cch"),
            "de_xpi_ind_energy_supply_services_idx": ("depric4754", "cch"),
            "de_xpi_ind_stones_soil_idx": ("depric4730", "cch"),
        },
        source_data="mb",
        component="Prices_Monetary",
        category="PM_Export_Prices",
        subcategory="PM_XPI_Industrial"
    )
)

NDv5.add(
    GroupSeries(
        series_dict = {
            "de_xpi_agri_products_idx": ("depric4724", "cch"),
            "de_xpi_forestry_products_idx": ("depric4725", "cch"),
            "de_xpi_fish_products_idx": ("depric4726", "cch"),
        },
        source_data="mb",
        component="Prices_Monetary",
        category="PM_Export_Prices",
        subcategory="PM_XPI_Agriculture"
    )
)

# --------------- Import Prices -------------------------------------------------------#

NDv5.add(
    GroupSeries(
        series_dict = {
            "de_mpi_total_idx": ("depric4690", "cch"),
            "de_mpi_ex_energy_idx": ("depric4955", "cch"),
            "de_mpi_ex_mineral_oil_idx": ("depric4948", "cch"),
            "de_mpi_ex_mineral_oil_products_idx": ("depric4947", "cch"),
            "de_mpi_ea_idx": ("depric4968", "cch"),
            "de_mpi_non_ea_idx": ("depric4969", "cch"),
        },
        source_data="mb",
        component="Prices_Monetary",
        category="PM_Import_Prices",
        subcategory="PM_MPI_Totals"
    )
)

NDv5.add(
    GroupSeries(
        series_dict = {
            "de_mpi_invest_goods_idx": ("depric4951", "cch"),
            "de_mpi_cons_goods_idx": ("depric4952", "cch"),
            "de_mpi_intermed_goods_idx": ("depric4950", "cch"),
            "de_mpi_dur_cons_goods_idx": ("depric4953", "cch"),
            "de_mpi_non_dur_cons_goods_idx": ("depric4954", "cch"),
            "de_mpi_energy_idx": ("depric4949", "cch"),
            "de_mpi_food_feed_bev_idx": ("depric4957", "cch"),
        },
        source_data="mb",
        component="Prices_Monetary",
        category="PM_Import_Prices",
        subcategory="PM_MPI_Goods_Categories"
    )
)

NDv5.add(
    GroupSeries(
        series_dict = {
            "de_mpi_egw_industrial_idx": ("depric4981", "cch"),
            "de_mpi_egw_raw_mat_idx": ("depric4979", "cch"),
            "de_mpi_egw_raw_semi_idx": ("depric4980", "cch"),
            "de_mpi_egw_semi_finished_idx": ("depric4982", "cch"),
            "de_mpi_egw_intermediate_idx": ("depric4983", "cch"),
            "de_mpi_egw_finished_idx": ("depric4984", "cch"),
            "de_mpi_egw_end_products_idx": ("depric4985", "cch"),
            "de_mpi_egw_food_total_idx": ("depric4974", "cch"),
            "de_mpi_egw_food_veg_idx": ("depric4976", "cch"),
            "de_mpi_egw_food_animal_idx": ("depric4973", "cch"),
            "de_mpi_egw_tea_coffee_tob_alc_idx": ("depric4978", "cch"),
        },
        source_data="mb",
        component="Prices_Monetary",
        category="PM_Import_Prices",
        subcategory="PM_MPI_EGW"
    )
)

NDv5.add(
    GroupSeries(
        series_dict = {
            "de_mpi_ind_mineral_resources_idx": ("depric4697", "cch"),
            "de_mpi_ind_oil_gas_idx": ("depric4696", "cch"),
            "de_mpi_ind_crude_oil_idx": ("depric4764", "cch"),
            "de_mpi_ind_natural_gas_idx": ("depric4765", "cch"),
            "de_mpi_ind_cokery_mineral_oil_idx": ("depric4707", "cch"),
            "de_mpi_ind_mineral_oil_products_idx": ("depric4793", "cch"),

            "de_mpi_ind_cars_parts_total_idx": ("depric4717", "cch"),
            "de_mpi_ind_motor_vehicles_idx": ("depric4839", "cch"),
            "de_mpi_ind_parts_accessories_idx": ("depric4841", "cch"),
            "de_mpi_ind_other_vehicles_total_idx": ("depric4718", "cch"),
            "de_mpi_ind_vehicles_nec_idx": ("depric4843", "cch"),

            "de_mpi_ind_machines_total_idx": ("depric4716", "cch"),
            "de_mpi_ind_machine_tools_idx": ("depric4837", "cch"),
            "de_mpi_ind_machines_other_unspecified_idx": ("depric4835", "cch"),
            "de_mpi_ind_machines_other_selected_branches_idx": ("depric4838", "cch"),

            "de_mpi_ind_electrical_mach_appar_total_idx": ("depric4715", "cch"),
            "de_mpi_ind_electrical_lamps_idx": ("depric4831", "cch"),
            "de_mpi_ind_household_appliances_idx": ("depric4832", "cch"),
            "de_mpi_ind_accumulators_batteries_idx": ("depric4829", "cch"),

            "de_mpi_ind_data_elec_optical_total_idx": ("depric4714", "cch"),
            "de_mpi_ind_consumer_electronics_idx": ("depric4824", "cch"),
            "de_mpi_ind_data_processing_devices_idx": ("depric4822", "cch"),
            "de_mpi_ind_measuring_control_navigation_clocks_idx": ("depric4825", "cch"),
            "de_mpi_ind_telecom_devices_equipment_idx": ("depric4823", "cch"),
            "de_mpi_ind_electromed_irradiation_devices_idx": ("depric4826", "cch"),
            
            "de_mpi_ind_chemicals_total_idx": ("depric4708", "cch"),
            "de_mpi_ind_chemical_fibers_idx": ("depric4799", "cch"),
            "de_mpi_ind_chem_primary_fertilizers_idx": ("depric4794", "cch"),
            "de_mpi_ind_coatings_printing_inks_putties_idx": ("depric4796", "cch"),

            "de_mpi_ind_pharma_total_idx": ("depric4709", "cch"),
            "de_mpi_ind_pharma_primary_other_idx": ("depric4800", "cch"),
            "de_mpi_ind_pharma_specialties_products_idx": ("depric4801", "cch"),

            "de_mpi_ind_rubber_plastic_total_idx": ("depric4710", "cch"),
            "de_mpi_ind_rubber_products_idx": ("depric4802", "cch"),

            "de_mpi_ind_paper_total_idx": ("depric4706", "cch"),
            "de_mpi_ind_pulp_paper_cardboard_idx": ("depric4790", "cch"),

            "de_mpi_ind_glass_ceramics_stone_total_idx": ("depric4711", "cch"),
            "de_mpi_ind_cement_lime_gypsum_idx": ("depric4808", "cch"),
            "de_mpi_ind_refractory_ceramics_idx": ("depric4805", "cch"),
            "de_mpi_ind_building_stones_processed_idx": ("depric4810", "cch"),
            "de_mpi_ind_non_metallic_minerals_nec_idx": ("depric4811", "cch"),

            "de_mpi_ind_stones_soil_total_idx": ("depric4698", "cch"),
            "de_mpi_ind_dimension_stones_gravel_sand_clay_kaolin_idx": ("depric4768", "cch"),
            "de_mpi_ind_stones_soils_nec_idx": ("depric4769", "cch"),

            "de_mpi_ind_metals_total_idx": ("depric4712", "cch"),
            "de_mpi_ind_raw_iron_steel_ferroalloys_idx": ("depric4812", "cch"),
            "de_mpi_ind_other_iron_steel_products_idx": ("depric4814", "cch"),
            "de_mpi_ind_nonferrous_metals_semifinished_idx": ("depric4815", "cch"),
            "de_mpi_ind_foundry_products_idx": ("depric4816", "cch"),

            "de_mpi_ind_metal_products_total_idx": ("depric4713", "cch"),
            "de_mpi_ind_steel_light_metal_construction_idx": ("depric4817", "cch"),
            "de_mpi_ind_other_metal_products_idx": ("depric4820", "cch"),

            "de_mpi_ind_textiles_total_idx": ("depric4702", "cch"),
            "de_mpi_ind_textile_spinning_yarns_idx": ("depric4781", "cch"),

            "de_mpi_ind_clothing_total_idx": ("depric4703", "cch"),
            "de_mpi_ind_clothing_ex_furs_idx": ("depric4784", "cch"),
            "de_mpi_ind_knitted_crocheted_clothing_idx": ("depric4785", "cch"),

            "de_mpi_ind_leather_footwear_idx": ("depric4787", "cch"),
            "de_mpi_ind_leather_ex_clothing_footwear_idx": ("depric4786", "cch"),

            "de_mpi_ind_wood_products_planed_sawed_idx": ("depric4788", "cch"),
            "de_mpi_ind_furniture_total_idx": ("depric4719", "cch"),

            "de_mpi_ind_beverages_total_idx": ("depric4700", "cch"),
            "de_mpi_ind_food_feed_total_idx": ("depric4699", "cch"),
            "de_mpi_ind_food_grain_milling_idx": ("depric4775", "cch"),
            "de_mpi_ind_food_fruits_vegetables_idx": ("depric4772", "cch"),
            "de_mpi_ind_food_meat_products_idx": ("depric4770", "cch"),
            "de_mpi_ind_food_pastries_pasta_idx": ("depric4776", "cch"),
            "de_mpi_ind_food_other_ex_bev_idx": ("depric4777", "cch"),
            "de_mpi_ind_oils_fats_idx": ("depric4773", "cch"),
            "de_mpi_ind_fish_seafood_idx": ("depric4771", "cch"),

            "de_mpi_ind_goods_nec_total_idx": ("depric4720", "cch"),
            "de_mpi_ind_goods_nec_med_dental_idx": ("depric4849", "cch"),
            "de_mpi_ind_goods_nec_toys_idx": ("depric4848", "cch"),
            "de_mpi_ind_goods_nec_musical_instruments_idx": ("depric4846", "cch"),
            "de_mpi_ind_goods_nec_sport_equipment_idx": ("depric4847", "cch"),
            "de_mpi_ind_goods_nec_other_products_idx": ("depric4850", "cch"),
        },
        source_data="mb",
        component="Prices_Monetary",
        category="PM_Import_Prices",
        subcategory="PM_MPI_Industrial"
    )
)

NDv5.add(
    GroupSeries(
        series_dict = {
            "de_mpi_agri_hunting_products_idx": ("depric4692", "cch"),
            "de_mpi_agri_live_animals_products_idx": ("depric4759", "cch"),
            "de_mpi_agri_raw_wood_idx": ("depric4760", "cch"),
            "de_mpi_agri_perennials_idx": ("depric4757", "cch"),
        },
        source_data="mb",
        component="Prices_Monetary",
        category="PM_Import_Prices",
        subcategory="PM_MPI_Agriculture"
    )
)

# -------------------------------------------------------------------------------------#
# --------------- Monetary Variables -------------------------------------------------#
# -------------------------------------------------------------------------------------#


NDv5.add(
    GroupSeries(
        series_dict={
            "de_bb_ms_m1_eur": ("buba_mb_154651", "cch"),
            "de_bb_ms_m2_eur": ("buba_mb_154652", "cch"),
            "de_bb_ms_m3_eur": ("buba_mb_154653", "cch"),
        },
        source_data="mb",
        component="Prices_Monetary",
        category="PM_Monetary_Variables",
        subcategory="PM_MV_Money_Supply"
    )
)


NDv5.add(
    GroupSeries(
        series_dict={
            "de_bb_fx_ecb_eur_gbp": ("buba_mb_44193", "cch"), 
            "de_bb_fx_ecb_eur_jpy": ("buba_mb_44185", "cch"), 
            "de_bb_fx_ecb_eur_usd": ("buba_mb_44166", "cch"), 
        },
        source_data="mb",
        component="Prices_Monetary",
        category="PM_Monetary_Variables",
        subcategory="PM_MV_Exchange_Rates"
    )
)

########################################################################################
# -------------------------------------------------------------------------------------#
# -------------------------------------------------------------------------------------#
# -------------------------------------------------------------------------------------#
# ----------------------------- FINANCIAL            ----------------------------------#
# ----------------------------- DATA                 ----------------------------------#
# -------------------------------------------------------------------------------------#
# -------------------------------------------------------------------------------------#
# -------------------------------------------------------------------------------------#
########################################################################################

# -------------------------------------------------------------------------------------#
# --------------- Yields --------------------------------------------------------------#
# -------------------------------------------------------------------------------------#

NDv5.add(
    GroupSeries(
        series_dict = {
            "de_gov_yld_1y_eop": ("de1ygov_m", "chg"),
            "de_gov_yld_2y_eop": ("de2ygov_m", "chg"),
            "de_gov_yld_3y_eop": ("de3ygov_m", "chg"),
            "de_gov_yld_4y_eop": ("de4ygov_m", "chg"),
            "de_gov_yld_5y_eop": ("de5ygov_m", "chg"),
            "de_gov_yld_6y_eop": ("de6ygov_m", "chg"),
            "de_gov_yld_7y_eop": ("de7ygov_m", "chg"),
            "de_gov_yld_8y_eop": ("de8ygov_m", "chg"),
            "de_gov_yld_9y_eop": ("de9ygov_m", "chg"),
            "de_gov_yld_10y_eop": ("de10ygov_m", "chg"),
            "de_gov_yld_11y_eop": ("de11ygov_m", "chg"),
            "de_gov_yld_12y_eop": ("de12ygov_m", "chg"),
            "de_gov_yld_13y_eop": ("de13ygov_m", "chg"),
            "de_gov_yld_14y_eop": ("de14ygov_m", "chg"),
            "de_gov_yld_15y_eop": ("de15ygov_m", "chg"),
        },
        source_data="mb",
        component="Financial_Markets",
        category="FM_Government_Bonds",
        subcategory="FM_GovBonds_DE_YieldCurve"
    )
)

NDv5.add(
    GroupSeries(
        series_dict = {
            "ea_gov_yld_10y": ("eues10ygov", "chg"),
            "us_gov_yld_10y_avg": ("us10yfedgov_m", "chg"),
            "dk_gov_yld_10y_eop": ("dk10ygov_m", "chg"),
            "fi_gov_yld_10y_avg": ("fi10ygov_m", "chg"),
            "jp_gov_yld_10y_eop": ("jp10ygov_m", "chg"),
            "gb_gov_yld_10y_eop": ("gb10ygov_m", "chg"),
            "se_gov_yld_10y_eop": ("se10ygov_m", "chg"),
            "ca_gov_yld_10y_eop": ("ca10ygov_m", "chg"),
            "fr_gov_yld_10y_eop": ("fr10ygov_m", "chg"),
            "it_gov_yld_10y_eop": ("it10ygov_m", "chg"),
            "ch_gov_yld_10y_eop": ("ch10ygov_m", "chg"),
            "es_gov_yld_10y_eop": ("es10ygov_m", "chg"),
            "nl_gov_yld_10y_eop": ("nl10ygov_m", "chg"),
            "ie_gov_yld_10y_eop": ("ie10ygov_m", "chg"),
            "pt_gov_yld_10y_eop": ("pt10ygov_m", "chg"),
            "be_gov_yld_10y_eop": ("be10ygov_m", "chg"),
            "gr_gov_yld_10y_eop": ("gr10ygov_m", "chg"),
            "at_gov_yld_10y_eop": ("at10ygov_m", "chg"),
        },
        source_data="mb",
        component="Financial_Markets",
        category="FM_Government_Bonds",
        subcategory="FM_GovBonds_10Y_Benchmarks"
    )
)

