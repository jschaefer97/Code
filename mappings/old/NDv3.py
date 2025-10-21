#%%

from data.seriesdataclass import Source, Series, GroupSeries
from data.nowdata import NOWData

#%%

NDv3 = NOWData("NDv3")

# -------------------------------------------------------------------------------------#
# --------------- National Accounts ---------------------------------------------------#
# -------------------------------------------------------------------------------------#

NDv3.add(
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
# --------------- Industrial Production -----------------------------------------------#
# -------------------------------------------------------------------------------------#

NDv3.add(
    GroupSeries(
        series_dict = {
            "de_ip_total_sa": ("deprod1404", "pch"),
            "de_ip_total_ex_constr_sa": ("deprod1370", "pch"),
            "de_ip_total_ex_energy_constr_sa": ("deprod1375", "pch"),
            "de_ip_total_ex_constr_foodbev_sa": ("deprod1398", "pch"),
            "de_ip_total_ex_energy_constr_othertrans_sa": ("deprod3695", "pch"),
            "de_ip_total_ex_energy_constr_energyint_sa": ("deprod3845", "pch"),
            "de_ip_total_ex_energy_constr_energyint_motorveh29_sa": ("deprod3846", "pch"),
            "de_ip_total_ex_energy_constr_motorveh29_sa": ("deprod3847", "pch"),
            "de_ip_total_ex_energy_constr_foodbev_elecgas_sa": ("deprod3690", "pch"),
        },
        source_data="mb",
        component="Hard_Data",
        category="HD_Industrial_Production",
        subcategory="HD_IP_Totals"
    )
)

NDv3.add(
    GroupSeries(
        series_dict = {
            "de_ip_intermed_sa": ("deprod1345", "pch"),
            "de_ip_capital_sa": ("deprod1350", "pch"),
            "de_ip_intermed_capital_sa": ("deprod3710", "pch"),
            "de_ip_consumer_sa": ("deprod1365", "pch"),
            "de_ip_consumer_durable_sa": ("deprod1355", "pch"),
            "de_ip_consumer_nondurable_sa": ("deprod1360", "pch"),
        },
        source_data="mb",
        component="Hard_Data",
        category="HD_Industrial_Production",
        subcategory="HD_IP_Goods_Aggregates"
    )
)

NDv3.add(
    GroupSeries(
        series_dict = {
            "de_ip_capital_ex_motorveh_sa": ("deprod3730", "pch"),
            "de_ip_capital_ex_motorveh_trailers_sa": ("deprod3715", "pch"),
            "de_ip_capital_ex_motorveh_trailers_othertrans_sa": ("deprod3725", "pch"),
            "de_ip_capital_ex_othertrans_sa": ("deprod3720", "pch"),
            "de_ip_capital_ex_airspace_sa": ("deprod3735", "pch"),
            "de_ip_capital_ex_motorveh_airspace_sa": ("deprod3740", "pch"),
            "de_ip_consumer_ex_foodbev_sa": ("deprod3745", "pch"),
        },
        source_data="mb",
        component="Hard_Data",
        category="HD_Industrial_Production",
        subcategory="HD_IP_Goods_Exclusions"
    )
)

NDv3.add(
    GroupSeries(
        series_dict = {
            "de_ip_energy_ex_waterwaste_sa": ("deprod1559", "pch"),
            "de_ip_energy_ex_elecgas_waterwaste_sa": ("deprod3665", "pch"),
            "de_ip_energyint_sa": ("deprod2997", "pch"),
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

NDv3.add(
    Series(
        name="de_ip_manu_total_sa",
        component="Hard_Data",
        category="HD_Manufacturing",
        subcategory="HD_MF_Manufacturing_Sectors",
        transformation="pch",
        source=Source(
            data="mb",
            variable="deprod1414"
        )
    )
)

NDv3.add(
    GroupSeries(
        series_dict = {
            "de_ip_mining_manu_total_sa": ("deprod1997", "pch"),
            "de_ip_manu_other_goods_sa": ("deprod0198", "pch"),
            "de_ip_manu_motorveh_trailers_sa": ("deprod0195", "pch"),
            "de_ip_manu_machinery_nec_sa": ("deprod0194", "pch"),
            "de_ip_manu_leather_sa": ("deprod0181", "pch"),
            "de_ip_manu_glass_ceramic_stone_sa": ("deprod0189", "pch"),
            "de_ip_manu_furniture_sa": ("deprod0197", "pch"),
            "de_ip_manu_food_sa": ("deprod0177", "pch"),
            "de_ip_manu_electrical_equip_sa": ("deprod0193", "pch"),
            "de_ip_manu_elec_optical_sa": ("deprod0192", "pch"),
            "de_ip_manu_clothes_sa": ("deprod0180", "pch"),
            "de_ip_manu_chemicals_sa": ("deprod0186", "pch"),
            "de_ip_manu_beverages_sa": ("deprod0178", "pch"),
            "de_ip_manu_basic_metals_sa": ("deprod0190", "pch"),
            "de_ip_manu_fabricated_metals_sa": ("deprod0191", "pch"),
            "de_ip_manu_other_transport_sa": ("deprod0196", "pch"),
            "de_ip_manu_paper_sa": ("deprod0183", "pch"),
            "de_ip_manu_pharma_sa": ("deprod0187", "pch"),
            "de_ip_manu_printing_sa": ("deprod0184", "pch"),
            "de_ip_manu_repair_install_sa": ("deprod0199", "pch"),
            "de_ip_manu_rubber_plastic_sa": ("deprod0188", "pch"),
            "de_ip_manu_textiles_sa": ("deprod0179", "pch"),
            "de_ip_manu_wood_sa": ("deprod0182", "pch"),
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

NDv3.add(
    Series(
        name="de_imp_total_destatis_sa",
        component="Hard_Data",
        category="HD_Foreign_Trade",
        subcategory="HD_FT_Imports_Total",
        transformation="pch",
        source=Source(
            data="mb",
            variable="detrad0689"
        )
    )
)

NDv3.add(
    Series(
        name="de_exp_total_destatis_sa",
        component="Hard_Data",
        category="HD_Foreign_Trade",
        subcategory="HD_FT_Exports_Total",
        transformation="pch",
        source=Source(
            data="mb",
            variable="detrad0692"
        )
    )
)

NDv3.add(
    Series(
        name="de_trade_bal_total_destatis_sa",
        component="Hard_Data",
        category="HD_Foreign_Trade",
        subcategory="HD_FT_Balance_Total",
        transformation="pch",
        source=Source(
            data="mb",
            variable="detrad0695"
        )
    )
)

# -------------------------------------------------------------------------------------#
# --------------- Trade: Imports ------------------------------------------------------#
# -------------------------------------------------------------------------------------#

NDv3.add(
    GroupSeries(
        series_dict = {
            "de_imp_europe_destatis_sa": ("detrad0711", "pch"),
            "de_imp_eu27exuk_destatis_sa": ("detrad0712", "pch"),
            "de_imp_ea18_destatis_sa": ("detrad0713", "pch"),
            "de_imp_other_eur_destatis_sa": ("detrad0714", "pch"),

            "de_imp_noneur_destatis_sa": ("detrad0715", "pch"),
            "de_imp_us_destatis_sa": ("detrad0716", "pch"),
            "de_imp_asia_destatis_sa": ("detrad0717", "pch"),
            "de_imp_opec_destatis_sa": ("detrad0718", "pch"),
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
NDv3.add(
    GroupSeries(
        series_dict = {
            "de_exp_eu27exuk_destatis_sa": ("detrad00001", "pch"),
            "de_exp_ea_destatis_sa": ("detrad00002", "pch"),
            "de_exp_nonea_destatis_sa": ("detrad00021", "pch"),
            "de_exp_non_eu_destatis_sa": ("detrad00030", "pch"),
            "de_exp_uk_destatis_sa": ("detrad00031", "pch"),
        },
        source_data="mb",
        component="Hard_Data",
        category="HD_Foreign_Trade",
        subcategory="HD_FT_Exports_ByRegion"
    )
)

# Countries
NDv3.add(
    GroupSeries(
        series_dict = {
            "de_exp_us_destatis_sa": ("detrad00039", "pch"),
            "de_exp_china_destatis_sa": ("detrad00040", "pch"),
            "de_exp_japan_destatis_sa": ("detrad00042", "pch"),
            "de_exp_india_destatis_sa": ("detrad00041", "pch"),
            "de_exp_switzerland_destatis_sa": ("detrad00034", "pch"),
            "de_exp_poland_destatis_sa": ("detrad00025", "pch"),
            "de_exp_france_destatis_sa": ("detrad00006", "pch"),
            "de_exp_netherlands_destatis_sa": ("detrad00014", "pch"),
            "de_exp_mexico_destatis_sa": ("detrad00038", "pch"),
            "de_exp_australia_destatis_sa": ("detrad00044", "pch"),
            "de_exp_turkey_destatis_sa": ("detrad00035", "pch"),
            "de_exp_south_korea_destatis_sa": ("detrad00043", "pch"),
            "de_exp_russia_destatis_sa": ("detrad00033", "pch"),
            "de_exp_norway_destatis_sa": ("detrad00032", "pch"),
            "de_exp_slovakia_destatis_sa": ("detrad00017", "pch"),
            "de_exp_hungary_destatis_sa": ("detrad00029", "pch"),
            "de_exp_brazil_destatis_sa": ("detrad00037", "pch"),
            "de_exp_czech_republic_destatis_sa": ("detrad00028", "pch"),
            "de_exp_italy_destatis_sa": ("detrad00009", "pch"),
            "de_exp_south_africa_destatis_sa": ("detrad00036", "pch"),
            "de_exp_ireland_destatis_sa": ("detrad00008", "pch"),
            "de_exp_romania_destatis_sa": ("detrad00026", "pch"),
            "de_exp_austria_destatis_sa": ("detrad00015", "pch"),
            "de_exp_denmark_destatis_sa": ("detrad00023", "pch"),
            "de_exp_spain_destatis_sa": ("detrad00019", "pch"),
            "de_exp_slovenia_destatis_sa": ("detrad00018", "pch"),
            "de_exp_belgium_destatis_sa": ("detrad00003", "pch"),
            "de_exp_sweden_destatis_sa": ("detrad00027", "pch"),
            "de_exp_cyprus_destatis_sa": ("detrad00020", "pch"),
            "de_exp_lithuania_destatis_sa": ("detrad00011", "pch"),
            "de_exp_greece_destatis_sa": ("detrad00007", "pch"),
            "de_exp_latvia_destatis_sa": ("detrad00010", "pch"),
            "de_exp_portugal_destatis_sa": ("detrad00016", "pch"),
            "de_exp_croatia_destatis_sa": ("detrad00024", "pch"),
            "de_exp_finland_destatis_sa": ("detrad00005", "pch"),
            "de_exp_estonia_destatis_sa": ("detrad00004", "pch"),
            "de_exp_bulgaria_destatis_sa": ("detrad00022", "pch"),
            "de_exp_malta_destatis_sa": ("detrad00013", "pch"),
            "de_exp_luxembourg_destatis_sa": ("detrad00012", "pch"),
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

NDv3.add(
    Series(
        name="de_dt_cons_turn_sa",
        component="Hard_Data",
        category="HD_Domestic_Trade",
        subcategory="HD_DT_Consumption_Related",
        transformation="pch",
        source=Source(
            data="mb",
            variable="detrad8161"
        )
    )
)

NDv3.add(
    Series(
        name="de_dt_cons_turn_sa",
        component="Hard_Data",
        category="HD_Domestic_Trade",
        subcategory="HD_DT_Vehicles",
        transformation="pch",
        source=Source(
            data="mb",
            variable="detrad1704"
        )
    )
)

# -------------------------------------------------------------------------------------#
# --------------- Construction --------------------------------------------------------#
# -------------------------------------------------------------------------------------#

NDv3.add(
    GroupSeries(
        series_dict = {
            "de_cstr_no_total_sa": ("deprod1633", "pch"),  
            "de_cstr_no_build_total_sa":  ("deprod1635", "pch"),
            "de_cstr_no_civil_total_sa":  ("deprod1643", "pch"),
        },
        source_data="mb",
        component="Hard_Data",
        category="HD_Construction",
        subcategory="HD_CSTR_Totals"
    )
)

NDv3.add(
    GroupSeries(
        series_dict = {
            "de_cstr_no_build_house_sa":     ("deprod1637", "pch"),
            "de_cstr_no_build_ex_house_sa":  ("deprod1639", "pch"),
        },
        source_data="mb",
        component="Hard_Data",
        category="HD_Construction",
        subcategory="HD_CSTR_Building"
    )
)

NDv3.add(
    GroupSeries(
        series_dict = {
            "de_cstr_no_road_build_sa":    ("deprod1645", "pch"),
            "de_cstr_no_civil_ex_road_sa": ("deprod1647", "pch"),
        },
        source_data="mb",
        component="Hard_Data",
        category="HD_Construction",
        subcategory="HD_CSTR_Civil"
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
NDv3.add(
    GroupSeries(
        series_dict = {
            "de_ifo_bs_total_expect_6m_bal_sa": ("desurv01051", "chg"),
            "de_ifo_bs_total_situation_bal_sa": ("desurv01050", "chg"),
            "de_ifo_bs_total_climate_avg_sa": ("desurv01049", "chg"),
        },
        source_data="mb",
        component="Soft_Data",
        category="SD_Business_Surveys",
        subcategory="SD_BS_Ifo_Headline"
    )
)

NDv3.add(
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

NDv3.add(
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

NDv3.add(
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

NDv3.add(
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

NDv3.add(
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

NDv3.add(
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

NDv3.add(
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

NDv3.add(
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

NDv3.add(
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

NDv3.add(
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

NDv3.add(
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

NDv3.add(
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

NDv3.add(
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

NDv3.add(
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

NDv3.add(
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

# -------------------------------------------------------------------------------------#
# --------------- GfK -----------------------------------------------------------------#
# -------------------------------------------------------------------------------------#

NDv3.add(
    GroupSeries(
        series_dict = {
            "de_gfk_cc_income_expect": ("desurv0027", None),
            "de_gfk_cc_econ_expect": ("desurv0026", None),
            "de_gfk_cc_willing_buy": ("desurv0028", None),
            "de_gfk_cc_indicator": ("desurv0029", None),
        },
        source_data="mb",
        component="Soft_Data",
        category="SD_Consumer_Surveys",
        subcategory="SD_CS_GfK_Consumer_Climate"
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

NDv3.add(
    GroupSeries(
        series_dict = {
            "de_cpi_total_idx": ("depric0001", "pch"),
            "de_cpi_core_idx": ("depric2458", "pch"),
            "de_cpi_goods_idx": ("depric2453", "pch"),
            "de_cpi_services_idx": ("depric2457", "pch"),
        },
        source_data="mb",
        component="Prices",
        category="PC_Consumer_Prices",
        subcategory="PC_CPI_Totals"
    )
)

NDv3.add(
    GroupSeries(
        series_dict = {
            "de_cpi_food_nonalc_idx": ("depric0671", "pch"),
            "de_cpi_housing_utilities_idx": ("depric0674", "pch"),
            "de_cpi_health_idx": ("depric0676", "pch"),
            "de_cpi_clothing_footwear_idx": ("depric0673", "pch"),
            "de_cpi_transport_idx": ("depric0677", "pch"),
            "de_cpi_rest_hotels_idx": ("depric0681", "pch"),
            "de_cpi_furn_household_idx": ("depric0675", "pch"),
            "de_cpi_misc_goods_services_idx": ("depric0682", "pch"),
            "de_cpi_communication_idx": ("depric0678", "pch"),
            "de_cpi_education_idx": ("depric0680", "pch"),
            "de_cpi_alc_tob_idx": ("depric0672", "pch"),
            "de_cpi_recreation_culture_idx": ("depric0679", "pch"),
        },
        source_data="mb",
        component="Prices",
        category="PC_Consumer_Prices",
        subcategory="PC_CPI_Sectors"
    )
)

# --------------- Export Prices -------------------------------------------------------#

NDv3.add(
    GroupSeries(
        series_dict = {
            "de_xpi_total_idx": ("depric4691", "pch"),
            "de_xpi_ex_energy_idx": ("depric4965", "pch"),
            "de_xpi_ea_idx": ("depric4970", "pch"),
            "de_xpi_non_ea_idx": ("depric4971", "pch"),
        },
        source_data="mb",
        component="Prices",
        category="PC_Export_Prices",
        subcategory="PC_XPI_Totals"
    )
)

NDv3.add(
    GroupSeries(
        series_dict = {
            "de_xpi_cons_goods_idx": ("depric4962", "pch"),
            "de_xpi_dur_cons_goods_idx": ("depric4963", "pch"),
            "de_xpi_non_dur_cons_goods_idx": ("depric4964", "pch"),
            "de_xpi_invest_goods_idx": ("depric4961", "pch"),
            "de_xpi_intermed_goods_idx": ("depric4960", "pch"),
            "de_xpi_energy_idx": ("depric4959", "pch"),
        },
        source_data="mb",
        component="Prices",
        category="PC_Export_Prices",
        subcategory="PC_XPI_Goods_Categories"
    )
)

NDv3.add(
    GroupSeries(
        series_dict = {
            "de_xpi_ind_machines_idx": ("depric4748", "pch"),
            "de_xpi_ind_cars_parts_idx": ("depric4749", "pch"),
            "de_xpi_ind_other_vehicles_idx": ("depric4750", "pch"),
            "de_xpi_ind_electrical_mach_appar_idx": ("depric4747", "pch"),
            "de_xpi_ind_data_elec_optical_idx": ("depric4746", "pch"),
            "de_xpi_ind_chemicals_idx": ("depric4740", "pch"),
            "de_xpi_ind_pharma_idx": ("depric4741", "pch"),
            "de_xpi_ind_rubber_plastic_idx": ("depric4742", "pch"),
            "de_xpi_ind_metal_products_idx": ("depric4745", "pch"),
            "de_xpi_ind_metals_idx": ("depric4744", "pch"),
            "de_xpi_ind_glass_ceramics_stone_idx": ("depric4743", "pch"),
            "de_xpi_ind_paper_idx": ("depric4738", "pch"),
            "de_xpi_ind_wood_products_idx": ("depric4737", "pch"),
            "de_xpi_ind_textiles_idx": ("depric4734", "pch"),
            "de_xpi_ind_clothing_idx": ("depric4735", "pch"),
            "de_xpi_ind_furniture_idx": ("depric4751", "pch"),
            "de_xpi_ind_beverages_idx": ("depric4732", "pch"),
            "de_xpi_ind_food_feed_idx": ("depric4731", "pch"),
            "de_xpi_ind_tobacco_idx": ("depric4733", "pch"),
            "de_xpi_ind_goods_nec_idx": ("depric4941", "pch"),
            "de_xpi_ind_oil_gas_idx": ("depric4728", "pch"),
            "de_xpi_ind_coal_idx": ("depric4727", "pch"),
            "de_xpi_ind_cokery_mineral_oil_idx": ("depric4739", "pch"),
            "de_xpi_ind_energy_supply_services_idx": ("depric4754", "pch"),
            "de_xpi_ind_stones_soil_idx": ("depric4730", "pch"),
        },
        source_data="mb",
        component="Prices",
        category="PC_Export_Prices",
        subcategory="PC_XPI_Industrial"
    )
)

NDv3.add(
    GroupSeries(
        series_dict = {
            "de_xpi_agri_products_idx": ("depric4724", "pch"),
            "de_xpi_forestry_products_idx": ("depric4725", "pch"),
            "de_xpi_fish_products_idx": ("depric4726", "pch"),
        },
        source_data="mb",
        component="Prices",
        category="PC_Export_Prices",
        subcategory="PC_XPI_Agriculture"
    )
)

# --------------- Import Prices -------------------------------------------------------#

NDv3.add(
    GroupSeries(
        series_dict = {
            "de_mpi_total_idx": ("depric4690", "pch"),
            "de_mpi_ex_energy_idx": ("depric4955", "pch"),
            "de_mpi_ex_mineral_oil_idx": ("depric4948", "pch"),
            "de_mpi_ex_mineral_oil_products_idx": ("depric4947", "pch"),
            "de_mpi_ea_idx": ("depric4968", "pch"),
            "de_mpi_non_ea_idx": ("depric4969", "pch"),
        },
        source_data="mb",
        component="Prices",
        category="PC_Import_Prices",
        subcategory="PC_MPI_Totals"
    )
)

NDv3.add(
    GroupSeries(
        series_dict = {
            "de_mpi_invest_goods_idx": ("depric4951", "pch"),
            "de_mpi_cons_goods_idx": ("depric4952", "pch"),
            "de_mpi_intermed_goods_idx": ("depric4950", "pch"),
            "de_mpi_dur_cons_goods_idx": ("depric4953", "pch"),
            "de_mpi_non_dur_cons_goods_idx": ("depric4954", "pch"),
            "de_mpi_energy_idx": ("depric4949", "pch"),
            "de_mpi_food_feed_bev_idx": ("depric4957", "pch"),
        },
        source_data="mb",
        component="Prices",
        category="PC_Import_Prices",
        subcategory="PC_MPI_Goods_Categories"
    )
)

NDv3.add(
    GroupSeries(
        series_dict = {
            "de_mpi_egw_industrial_idx": ("depric4981", "pch"),
            "de_mpi_egw_raw_mat_idx": ("depric4979", "pch"),
            "de_mpi_egw_raw_semi_idx": ("depric4980", "pch"),
            "de_mpi_egw_semi_finished_idx": ("depric4982", "pch"),
            "de_mpi_egw_intermediate_idx": ("depric4983", "pch"),
            "de_mpi_egw_finished_idx": ("depric4984", "pch"),
            "de_mpi_egw_end_products_idx": ("depric4985", "pch"),
            "de_mpi_egw_food_total_idx": ("depric4974", "pch"),
            "de_mpi_egw_food_veg_idx": ("depric4976", "pch"),
            "de_mpi_egw_food_animal_idx": ("depric4973", "pch"),
            "de_mpi_egw_tea_coffee_tob_alc_idx": ("depric4978", "pch"),
        },
        source_data="mb",
        component="Prices",
        category="PC_Import_Prices",
        subcategory="PC_MPI_EGW"
    )
)

NDv3.add(
    GroupSeries(
        series_dict = {
            "de_mpi_ind_mineral_resources_idx": ("depric4697", "pch"),
            "de_mpi_ind_oil_gas_idx": ("depric4696", "pch"),
            "de_mpi_ind_crude_oil_idx": ("depric4764", "pch"),
            "de_mpi_ind_natural_gas_idx": ("depric4765", "pch"),
            "de_mpi_ind_cokery_mineral_oil_idx": ("depric4707", "pch"),
            "de_mpi_ind_mineral_oil_products_idx": ("depric4793", "pch"),

            "de_mpi_ind_cars_parts_total_idx": ("depric4717", "pch"),
            "de_mpi_ind_motor_vehicles_idx": ("depric4839", "pch"),
            "de_mpi_ind_car_bodies_trailers_idx": ("depric4840", "pch"),
            "de_mpi_ind_parts_accessories_idx": ("depric4841", "pch"),
            "de_mpi_ind_other_vehicles_total_idx": ("depric4718", "pch"),
            "de_mpi_ind_rail_vehicles_idx": ("depric4842", "pch"),
            "de_mpi_ind_vehicles_nec_idx": ("depric4843", "pch"),

            "de_mpi_ind_machines_total_idx": ("depric4716", "pch"),
            "de_mpi_ind_machine_tools_idx": ("depric4837", "pch"),
            "de_mpi_ind_machines_other_unspecified_idx": ("depric4835", "pch"),
            "de_mpi_ind_machines_other_selected_branches_idx": ("depric4838", "pch"),

            "de_mpi_ind_electrical_mach_appar_total_idx": ("depric4715", "pch"),
            "de_mpi_ind_electrical_engines_generators_transformers_idx": ("depric4828", "pch"),
            "de_mpi_ind_electrical_lamps_idx": ("depric4831", "pch"),
            "de_mpi_ind_household_appliances_idx": ("depric4832", "pch"),
            "de_mpi_ind_other_electrical_appliances_idx": ("depric4833", "pch"),
            "de_mpi_ind_accumulators_batteries_idx": ("depric4829", "pch"),

            "de_mpi_ind_data_elec_optical_total_idx": ("depric4714", "pch"),
            "de_mpi_ind_consumer_electronics_idx": ("depric4824", "pch"),
            "de_mpi_ind_data_processing_devices_idx": ("depric4822", "pch"),
            "de_mpi_ind_measuring_control_navigation_clocks_idx": ("depric4825", "pch"),
            "de_mpi_ind_telecom_devices_equipment_idx": ("depric4823", "pch"),
            "de_mpi_ind_electromed_irradiation_devices_idx": ("depric4826", "pch"),
            
            "de_mpi_ind_chemicals_total_idx": ("depric4708", "pch"),
            "de_mpi_ind_chemical_fibers_idx": ("depric4799", "pch"),
            "de_mpi_ind_chem_primary_fertilizers_idx": ("depric4794", "pch"),
            "de_mpi_ind_coatings_printing_inks_putties_idx": ("depric4796", "pch"),

            "de_mpi_ind_pharma_total_idx": ("depric4709", "pch"),
            "de_mpi_ind_pharma_primary_other_idx": ("depric4800", "pch"),
            "de_mpi_ind_pharma_specialties_products_idx": ("depric4801", "pch"),

            "de_mpi_ind_rubber_plastic_total_idx": ("depric4710", "pch"),
            "de_mpi_ind_rubber_products_idx": ("depric4802", "pch"),

            "de_mpi_ind_paper_total_idx": ("depric4706", "pch"),
            "de_mpi_ind_pulp_paper_cardboard_idx": ("depric4790", "pch"),

            "de_mpi_ind_glass_ceramics_stone_total_idx": ("depric4711", "pch"),
            "de_mpi_ind_cement_lime_gypsum_idx": ("depric4808", "pch"),
            "de_mpi_ind_refractory_ceramics_idx": ("depric4805", "pch"),
            "de_mpi_ind_building_stones_processed_idx": ("depric4810", "pch"),
            "de_mpi_ind_non_metallic_minerals_nec_idx": ("depric4811", "pch"),

            "de_mpi_ind_stones_soil_total_idx": ("depric4698", "pch"),
            "de_mpi_ind_dimension_stones_gravel_sand_clay_kaolin_idx": ("depric4768", "pch"),
            "de_mpi_ind_stones_soils_nec_idx": ("depric4769", "pch"),

            "de_mpi_ind_metals_total_idx": ("depric4712", "pch"),
            "de_mpi_ind_raw_iron_steel_ferroalloys_idx": ("depric4812", "pch"),
            "de_mpi_ind_other_iron_steel_products_idx": ("depric4814", "pch"),
            "de_mpi_ind_nonferrous_metals_semifinished_idx": ("depric4815", "pch"),
            "de_mpi_ind_foundry_products_idx": ("depric4816", "pch"),

            "de_mpi_ind_metal_products_total_idx": ("depric4713", "pch"),
            "de_mpi_ind_steel_light_metal_construction_idx": ("depric4817", "pch"),
            "de_mpi_ind_other_metal_products_idx": ("depric4820", "pch"),

            "de_mpi_ind_textiles_total_idx": ("depric4702", "pch"),
            "de_mpi_ind_textile_spinning_yarns_idx": ("depric4781", "pch"),

            "de_mpi_ind_clothing_total_idx": ("depric4703", "pch"),
            "de_mpi_ind_clothing_ex_furs_idx": ("depric4784", "pch"),
            "de_mpi_ind_knitted_crocheted_clothing_idx": ("depric4785", "pch"),

            "de_mpi_ind_leather_footwear_idx": ("depric4787", "pch"),
            "de_mpi_ind_leather_ex_clothing_footwear_idx": ("depric4786", "pch"),

            "de_mpi_ind_wood_products_planed_sawed_idx": ("depric4788", "pch"),
            "de_mpi_ind_furniture_total_idx": ("depric4719", "pch"),

            "de_mpi_ind_beverages_total_idx": ("depric4700", "pch"),
            "de_mpi_ind_food_feed_total_idx": ("depric4699", "pch"),
            "de_mpi_ind_food_grain_milling_idx": ("depric4775", "pch"),
            "de_mpi_ind_food_fruits_vegetables_idx": ("depric4772", "pch"),
            "de_mpi_ind_food_meat_products_idx": ("depric4770", "pch"),
            "de_mpi_ind_food_pastries_pasta_idx": ("depric4776", "pch"),
            "de_mpi_ind_food_other_ex_bev_idx": ("depric4777", "pch"),
            "de_mpi_ind_oils_fats_idx": ("depric4773", "pch"),
            "de_mpi_ind_fish_seafood_idx": ("depric4771", "pch"),

            "de_mpi_ind_goods_nec_total_idx": ("depric4720", "pch"),
            "de_mpi_ind_goods_nec_med_dental_idx": ("depric4849", "pch"),
            "de_mpi_ind_goods_nec_toys_idx": ("depric4848", "pch"),
            "de_mpi_ind_goods_nec_musical_instruments_idx": ("depric4846", "pch"),
            "de_mpi_ind_goods_nec_sport_equipment_idx": ("depric4847", "pch"),
            "de_mpi_ind_goods_nec_other_products_idx": ("depric4850", "pch"),
        },
        source_data="mb",
        component="Prices",
        category="PC_Import_Prices",
        subcategory="PC_MPI_Industrial"
    )
)

NDv3.add(
    GroupSeries(
        series_dict = {
            "de_mpi_agri_hunting_products_idx": ("depric4692", "pch"),
            "de_mpi_agri_live_animals_products_idx": ("depric4759", "pch"),
            "de_mpi_agri_fish_fishery_products_idx": ("depric4694", "pch"),
            "de_mpi_agri_raw_wood_idx": ("depric4760", "pch"),
            "de_mpi_agri_perennials_idx": ("depric4757", "pch"),
            "de_mpi_agri_wild_non_wood_products_idx": ("depric4761", "pch"),
        },
        source_data="mb",
        component="Prices",
        category="PC_Import_Prices",
        subcategory="PC_MPI_Agriculture"
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

NDv3.add(
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

NDv3.add(
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

