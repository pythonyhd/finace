# -*- coding: utf-8 -*-

xpath_list = [
    {
        "name": "行政区:",
        'key': "region",
        "expr": ["//div[@id='p1']//td/span[contains(text(),'行政区:')]/parent::td/following-sibling::td[1]/span/text()",
                 "//span[@id='mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r1_c2_ctrl']/text()"]
    },
    {
        "name": "电子监管号：",
        "key": "supervise_number",
        "expr": ["//div[@id='p1']//td/span[contains(text(),'电子监管号：')]/parent::td/following-sibling::td[1]/span/text()",
                 "//span[@id='mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r1_c4_ctrl']/text()"]
    },
    {
        "name": "项目名称",
        "key": "project_name",
        "expr": ["//div[@id='p1']//td/span[contains(text(),'项目名称:')]/parent::td/following-sibling::td[1]/span/text()",
                 "//span[@id='mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r17_c2_ctrl']/text()"],
    },
    {
        "name": "项目位置:",
        "key": "project_location",
        "expr": ["//div[@id='p1']//td/span[contains(text(),'项目位置:')]/parent::td/following-sibling::td[1]/span/text()",
                 "//span[@id='mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r16_c2_ctrl']/text()"],
    },
    {
        "name": "面积(公顷):",
        "key": "acreage",
        "expr": ["//div[@id='p1']//td/span[contains(text(),'面积(公顷):')]/parent::td/following-sibling::td[1]/span/text()",
                 "//span[@id='mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r2_c2_ctrl']/text()"]
    },
    {
        "name": "土地来源:",
        "key": "source",
        "expr": ["//div[@id='p1']//td/span[contains(text(),'土地来源:')]/parent::td/following-sibling::td[1]/span/text()",
                 "//span[@id='mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r2_c2_ctrl']/text()"],
    },
    {
        "name": "土地用途:",
        "key": "purpose",
        "expr": ["//div[@id='p1']//td/span[contains(text(),'土地用途:')]/parent::td/following-sibling::td[1]/span/text()",
                 "//span[@id='mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r3_c2_ctrl']/text()"]
    },
    {
        "name": "供地方式:",
        "key": "supply",
        "expr": ["//div[@id='p1']//td/span[contains(text(),'供地方式:')]/parent::td/following-sibling::td[1]/span/text()",
                 "//span[@id='mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r3_c4_ctrl']/text()"]
    },
    {
        "name": "土地使用年限:",
        "key": "soil_life",
        "expr": ["//div[@id='p1']//td/span[contains(text(),'土地使用年限:')]/parent::td/following-sibling::td[1]/span/text()",
                 "//span[@id='mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r19_c2_ctrl']/text()"]
    },
    {
        "name": "行业分类:",
        "key": "classification",
        "expr": ["//div[@id='p1']//td/span[contains(text(),'行业分类:')]/parent::td/following-sibling::td[1]/span/text()",
                 "//span[@id='mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r19_c4_ctrl']/text()"]
    },
    {
        "name": "土地级别:",
        "key": "soil_level",
        "expr": ["//div[@id='p1']//td/span[contains(text(),'土地级别:')]/parent::td/following-sibling::td[1]/span/text()",
                 "//span[@id='mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r20_c2_ctrl']/text()"]
    },
    {
        "name": "成交价格(万元):",
        "key": "price",
        "expr": [
            "//div[@id='p1']//td/span[contains(text(),'成交价格(万元):')]/parent::td/following-sibling::td[1]/span/text()",
            "//span[@id='mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r20_c4_ctrl']/text()"]
    },
    {
        "name": "土地使用权人:",
        "key": "land_usage_right",
        "expr": ["//div[@id='p1']//td/span[contains(text(),'土地使用权人:')]/parent::td/following-sibling::td[1]/span/text()",
                 "//span[@id='mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r23_c2_ctrl']/text()"]
    },
    {
        "name": "下限:",
        "key": "lower_limit",
        "expr": ["//div[@id='p1']//td/span[contains(text(),'下限:')]/parent::td/following-sibling::td[1]/span/text()",
                 "//span[@id='mainModuleContainer_1855_1856_ctl00_ctl00_p1_f2_r1_c2_ctrl']/text()"]
    },
    {
        "name": "上限:",
        "key": "upper_limit",
        "expr": ["//div[@id='p1']//td/span[contains(text(),'上限:')]/parent::td/following-sibling::td[1]/span/text()",
                 "//span[@id='mainModuleContainer_1855_1856_ctl00_ctl00_p1_f2_r1_c4_ctrl']/text()"]
    },
    {
        "name": "约定交地时间:",
        "key": "appointed_deal_date",
        "expr": ["//div[@id='p1']//td/span[contains(text(),'约定交地时间:')]/parent::td/following-sibling::td[1]/span/text()",
                 "//span[@id='mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r21_c4_ctrl']/text()"]
    },
    {
        "name": "约定开工时间:",
        "key": "appointed_work_date",
        "expr": ["//div[@id='p1']//td/span[contains(text(),'约定开工时间:')]/parent::td/following-sibling::td[1]/span/text()",
                 "//span[@id='mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r22_c2_ctrl']/text()"]
    },
    {
        "name": "约定竣工时间:",
        "key": "appointed_achieve_date",
        "expr": ["//div[@id='p1']//td/span[contains(text(),'约定竣工时间:')]/parent::td/following-sibling::td[1]/span/text()",
                 "//span[@id='mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r22_c4_ctrl']/text()"]
    },
    {
        "name": "实际开工时间:",
        "key": "reality_work_date",
        "expr": ["//div[@id='p1']//td/span[contains(text(),'实际开工时间:')]/parent::td/following-sibling::td[1]/span/text()",
                 "//span[@id='mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r10_c2_ctrl']/text()"]
    },
    {
        "name": "实际竣工时间:",
        "key": "reality_achieve_date",
        "expr": ["//div[@id='p1']//td/span[contains(text(),'实际竣工时间:')]/parent::td/following-sibling::td[1]/span/text()",
                 "//span[@id='mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r22_c4_ctrl']/text()"]
    },
    {
        "name": "批准单位:",
        "key": "approved",
        "expr": ["//div[@id='p1']//td/span[contains(text(),'批准单位:')]/parent::td/following-sibling::td[1]/span/text()",
                 "//span[@id='mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r14_c2_ctrl']/text()"]
    },
    {
        "name": "合同签订日期:",
        "key": "contract_date",
        "expr": ["//div[@id='p1']//td/span[contains(text(),'合同签订日期:')]/parent::td/following-sibling::td[1]/span/text()",
                 "//span[@id='mainModuleContainer_1855_1856_ctl00_ctl00_p1_f1_r14_c4_ctrl']/text()"]
    },

]
