# -*- coding: utf-8 -*-

# 融360-贷款列表页
rong_list_settings = {
    "RETRY_ENABLED": True,
    "RETRY_TIMES": '9',
    "DOWNLOAD_TIMEOUT": '30',

    "ITEM_PIPELINES": {
        "finace.pipelines.FinacePipeline": 340,
        "finace.pipelines.MongodbIndexPipeline": 350,
    },

    "DOWNLOADER_MIDDLEWARES": {
        "finace.middlewares.RandomUserAgentMiddleware": 400,
    },
}


# 融360-城市列表
rong_city_settings = {
    "RETRY_ENABLED": True,
    "RETRY_TIMES": '9',
    "DOWNLOAD_TIMEOUT": '30',

    "ITEM_PIPELINES": {
        "finace.pipelines.MongodbIndexPipeline": 340,
    },

    "DOWNLOADER_MIDDLEWARES": {
        "finace.middlewares.RandomUserAgentMiddleware": 400,
    },
}