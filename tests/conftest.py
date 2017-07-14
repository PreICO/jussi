# -*- coding: utf-8 -*-

import os

import ujson
from aiocache import SimpleMemoryCache
from sanic import Sanic

import jsonschema
import jussi.errors
import jussi.handlers
import jussi.listeners
import jussi.logging_config
import jussi.middlewares
import jussi.serve
import pytest

TEST_DIR = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(TEST_DIR, 'request-schema.json')) as f:
    REQUEST_SCHEMA = ujson.load(f)
with open(os.path.join(TEST_DIR, 'response-schema.json')) as f:
    RESPONSE_SCHEMA = ujson.load(f)

INVALID_JRPC_REQUESTS = [
    # bad/missing jsonrpc
    {
        'id': 1,
        'method': 'get_block',
        'params': [1000]
    },
    {
        'id': 1,
        'jsonrpc': 2.0,
        'method': 'get_block',
        'params': [1000]
    },
    {
        'id': 1,
        'json-rpc': '2.0',
        'method': 'get_block',
        'params': [1000]
    },
    {
        'id': 1,
        'json_rpc': '2.0',
        'method': 'get_block',
        'params': [1000]
    },
    {
        'id': 1,
        'json_rpc': ['2.0'],
        'method': 'get_block',
        'params': [1000]
    },
    {
        'id': 1,
        'jsonrpc': None,
        'method': 'get_block',
        'params': [1000]
    },

    # bad/missing id
    {
        'id': None,
        'json_rpc': '2.0',
        'method': 'get_block',
        'params': [1000]
    },
    {
        'ID': 1,
        'json_rpc': '2.0',
        'method': 'get_block',
        'params': [1000]
    },
    {
        'Id': 1,
        'json_rpc': '2.0',
        'method': 'get_block',
        'params': [1000]
    },
    {
        'id': [1],
        'json_rpc': '2.0',
        'method': 'get_block',
        'params': [1000]
    },
    {
        'id': None,
        'json_rpc': '2.0',
        'method': 'get_block',
        'params': [1000]
    },

    # bad params
    {
        'id': 1,
        'json_rpc': '2.0',
        'method': 'get_block',
        'params': 1000
    },
    {
        'id': 1,
        'json_rpc': '2.0',
        'method': 'get_block',
        'params': '1000'
    },
    {
        'id': 1,
        'json_rpc': '2.0',
        'method': 'get_block',
        'params': None
    },

    # bad/missing method
    {
        'id': 1,
        'json_rpc': '2.0',
        'params': [1000]
    },
    {
        'id': 1,
        'json_rpc': '2.0',
        'METHOD': 'get_block',
        'params': '1000'
    },
    {
        'id': 1,
        'json_rpc': '2.0',
        'method': ['get_block'],
        'params': '1000'
    },
    {
        'id': 1,
        'json_rpc': '2.0',
        'method': None,
        'params': '1000'
    },
]

VALID_JRPC_REQUESTS = [{
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'get_account_count',
    'params': []
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'get_account_history',
    'params': ['steemit', 10, 20]
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'get_account_references',
    'params': ['steemit']
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'get_account_votes',
    'params': []
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'get_accounts',
    'params': ['steemit']
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'get_active_categories',
    'params': ['steemit', 10]
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'get_active_votes',
    'params': ['steemit', 'steemit']
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'get_active_witnesses',
    'params': []
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'get_best_categories',
    'params': ['steemit', 10]
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'get_block_header',
    'params': [1000]
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'get_chain_properties',
    'params': []
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'get_config',
    'params': []
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'get_content',
    'params': ['steemit']
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'get_content_replies',
    'params': ['steemit']
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'get_conversion_requests',
    'params': ['steemit']
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'get_current_median_history_price',
    'params': []
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'get_discussions_by_active',
    'params': ['steemit', 10]
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'get_discussions_by_author_before_date',
    'params': []
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'get_discussions_by_cashout',
    'params': ['steemit', 10]
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'get_discussions_by_children',
    'params': ['steemit', 10]
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'get_discussions_by_created',
    'params': ['steemit', 10]
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'get_discussions_by_feed',
    'params': ['steemit', 10]
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'get_discussions_by_hot',
    'params': ['steemit', 10]
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'get_discussions_by_payout',
    'params': ['steemit', 10]
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'get_discussions_by_trending',
    'params': ['steemit', 10]
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'get_discussions_by_votes',
    'params': ['steemit', 10]
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'get_dynamic_global_properties',
    'params': []
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'get_feed_history',
    'params': []
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'get_hardfork_version',
    'params': []
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'get_key_references',
    'params': []
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'get_liquidity_queue',
    'params': ['steemit', 10]
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'get_miner_queue',
    'params': []
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'get_next_scheduled_hardfork',
    'params': ['steemit', 10]
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'get_open_orders',
    'params': ['steemit']
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'get_order_book',
    'params': [10]
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'get_owner_history',
    'params': ['steemit']
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'get_recent_categories',
    'params': ['steemit', 10]
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'get_recovery_request',
    'params': ['steemit']
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'get_replies_by_last_update',
    'params': []
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'get_state',
    'params': []
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'get_transaction',
    'params': []
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'get_trending_categories',
    'params': []
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'get_trending_tags',
    'params': ['steemit', 10]
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'get_witness_by_account',
    'params': ['smooth.witness']
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'get_witness_count',
    'params': []
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'get_witness_schedule',
    'params': []
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'lookup_account_names',
    'params': ['steemit']
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'lookup_accounts',
    'params': ['steemit', 10]
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'lookup_witness_accounts',
    'params': ['steemit', 10]
}]

STEEMD_JSON_RPC_CALLS = [{
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'call',
    'params': ['database_api', 'get_account_count', []]
}, {
    'id':
    1,
    'jsonrpc':
    '2.0',
    'method':
    'call',
    'params': ['database_api', 'get_account_history', ['steemit', 10, 20]]
}, {
    'id':
    1,
    'jsonrpc':
    '2.0',
    'method':
    'call',
    'params': ['database_api', 'get_account_references', ['steemit']]
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'call',
    'params': ['database_api', 'get_account_votes', []]
}, {
    'id':
    1,
    'jsonrpc':
    '2.0',
    'method':
    'call',
    'params': ['database_api', 'get_accounts', ['steemit']]
}, {
    'id':
    1,
    'jsonrpc':
    '2.0',
    'method':
    'call',
    'params': ['database_api', 'get_active_categories', ['steemit', 10]]
}, {
    'id':
    1,
    'jsonrpc':
    '2.0',
    'method':
    'call',
    'params': ['database_api', 'get_active_votes', ['steemit', 'steemit']]
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'call',
    'params': ['database_api', 'get_active_witnesses', []]
}, {
    'id':
    1,
    'jsonrpc':
    '2.0',
    'method':
    'call',
    'params': ['database_api', 'get_best_categories', ['steemit', 10]]
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'call',
    'params': ['database_api', 'get_block_header', [1000]]
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'call',
    'params': ['database_api', 'get_chain_properties', []]
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'call',
    'params': ['database_api', 'get_config', []]
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'call',
    'params': ['database_api', 'get_content', ['steemit']]
}, {
    'id':
    1,
    'jsonrpc':
    '2.0',
    'method':
    'call',
    'params': ['database_api', 'get_content_replies', ['steemit']]
}, {
    'id':
    1,
    'jsonrpc':
    '2.0',
    'method':
    'call',
    'params': ['database_api', 'get_conversion_requests', ['steemit']]
}, {
    'id':
    1,
    'jsonrpc':
    '2.0',
    'method':
    'call',
    'params': ['database_api', 'get_current_median_history_price', []]
}, {
    'id':
    1,
    'jsonrpc':
    '2.0',
    'method':
    'call',
    'params': ['database_api', 'get_discussions_by_active', ['steemit', 10]]
}, {
    'id':
    1,
    'jsonrpc':
    '2.0',
    'method':
    'call',
    'params': ['database_api', 'get_discussions_by_author_before_date', []]
}, {
    'id':
    1,
    'jsonrpc':
    '2.0',
    'method':
    'call',
    'params': ['database_api', 'get_discussions_by_cashout', ['steemit', 10]]
}, {
    'id':
    1,
    'jsonrpc':
    '2.0',
    'method':
    'call',
    'params': ['database_api', 'get_discussions_by_children', ['steemit', 10]]
}, {
    'id':
    1,
    'jsonrpc':
    '2.0',
    'method':
    'call',
    'params': ['database_api', 'get_discussions_by_created', ['steemit', 10]]
}, {
    'id':
    1,
    'jsonrpc':
    '2.0',
    'method':
    'call',
    'params': ['database_api', 'get_discussions_by_feed', ['steemit', 10]]
}, {
    'id':
    1,
    'jsonrpc':
    '2.0',
    'method':
    'call',
    'params': ['database_api', 'get_discussions_by_hot', ['steemit', 10]]
}, {
    'id':
    1,
    'jsonrpc':
    '2.0',
    'method':
    'call',
    'params': ['database_api', 'get_discussions_by_payout', ['steemit', 10]]
}, {
    'id':
    1,
    'jsonrpc':
    '2.0',
    'method':
    'call',
    'params': ['database_api', 'get_discussions_by_trending', ['steemit', 10]]
}, {
    'id':
    1,
    'jsonrpc':
    '2.0',
    'method':
    'call',
    'params': ['database_api', 'get_discussions_by_votes', ['steemit', 10]]
}, {
    'id':
    1,
    'jsonrpc':
    '2.0',
    'method':
    'call',
    'params': ['database_api', 'get_dynamic_global_properties', []]
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'call',
    'params': ['database_api', 'get_feed_history', []]
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'call',
    'params': ['database_api', 'get_hardfork_version', []]
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'call',
    'params': ['database_api', 'get_key_references', []]
}, {
    'id':
    1,
    'jsonrpc':
    '2.0',
    'method':
    'call',
    'params': ['database_api', 'get_liquidity_queue', ['steemit', 10]]
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'call',
    'params': ['database_api', 'get_miner_queue', []]
}, {
    'id':
    1,
    'jsonrpc':
    '2.0',
    'method':
    'call',
    'params': ['database_api', 'get_next_scheduled_hardfork', ['steemit', 10]]
}, {
    'id':
    1,
    'jsonrpc':
    '2.0',
    'method':
    'call',
    'params': ['database_api', 'get_open_orders', ['steemit']]
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'call',
    'params': ['database_api', 'get_order_book', [10]]
}, {
    'id':
    1,
    'jsonrpc':
    '2.0',
    'method':
    'call',
    'params': ['database_api', 'get_owner_history', ['steemit']]
}, {
    'id':
    1,
    'jsonrpc':
    '2.0',
    'method':
    'call',
    'params': ['database_api', 'get_recent_categories', ['steemit', 10]]
}, {
    'id':
    1,
    'jsonrpc':
    '2.0',
    'method':
    'call',
    'params': ['database_api', 'get_recovery_request', ['steemit']]
}, {
    'id':
    1,
    'jsonrpc':
    '2.0',
    'method':
    'call',
    'params': ['database_api', 'get_replies_by_last_update', []]
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'call',
    'params': ['database_api', 'get_state', []]
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'call',
    'params': ['database_api', 'get_transaction', []]
}, {
    'id':
    1,
    'jsonrpc':
    '2.0',
    'method':
    'call',
    'params': ['database_api', 'get_trending_categories', []]
}, {
    'id':
    1,
    'jsonrpc':
    '2.0',
    'method':
    'call',
    'params': ['database_api', 'get_trending_tags', ['steemit', 10]]
}, {
    'id':
    1,
    'jsonrpc':
    '2.0',
    'method':
    'call',
    'params': ['database_api', 'get_witness_by_account', ['smooth.witness']]
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'call',
    'params': ['database_api', 'get_witness_count', []]
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'call',
    'params': ['database_api', 'get_witness_schedule', []]
}, {
    'id':
    1,
    'jsonrpc':
    '2.0',
    'method':
    'call',
    'params': ['database_api', 'lookup_account_names', ['steemit']]
}, {
    'id':
    1,
    'jsonrpc':
    '2.0',
    'method':
    'call',
    'params': ['database_api', 'lookup_accounts', ['steemit', 10]]
}, {
    'id':
    1,
    'jsonrpc':
    '2.0',
    'method':
    'call',
    'params': ['database_api', 'lookup_witness_accounts', ['steemit', 10]]
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'get_account_count',
    'params': []
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'get_account_history',
    'params': ['steemit', 10, 20]
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'get_account_references',
    'params': ['steemit']
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'get_account_votes',
    'params': []
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'get_accounts',
    'params': ['steemit']
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'get_active_categories',
    'params': ['steemit', 10]
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'get_active_votes',
    'params': ['steemit', 'steemit']
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'get_active_witnesses',
    'params': []
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'get_best_categories',
    'params': ['steemit', 10]
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'get_block_header',
    'params': [1000]
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'get_chain_properties',
    'params': []
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'get_config',
    'params': []
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'get_content',
    'params': ['steemit']
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'get_content_replies',
    'params': ['steemit']
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'get_conversion_requests',
    'params': ['steemit']
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'get_current_median_history_price',
    'params': []
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'get_discussions_by_active',
    'params': ['steemit', 10]
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'get_discussions_by_author_before_date',
    'params': []
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'get_discussions_by_cashout',
    'params': ['steemit', 10]
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'get_discussions_by_children',
    'params': ['steemit', 10]
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'get_discussions_by_created',
    'params': ['steemit', 10]
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'get_discussions_by_feed',
    'params': ['steemit', 10]
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'get_discussions_by_hot',
    'params': ['steemit', 10]
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'get_discussions_by_payout',
    'params': ['steemit', 10]
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'get_discussions_by_trending',
    'params': ['steemit', 10]
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'get_discussions_by_votes',
    'params': ['steemit', 10]
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'get_dynamic_global_properties',
    'params': []
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'get_feed_history',
    'params': []
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'get_hardfork_version',
    'params': []
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'get_key_references',
    'params': []
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'get_liquidity_queue',
    'params': ['steemit', 10]
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'get_miner_queue',
    'params': []
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'get_next_scheduled_hardfork',
    'params': ['steemit', 10]
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'get_open_orders',
    'params': ['steemit']
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'get_order_book',
    'params': [10]
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'get_owner_history',
    'params': ['steemit']
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'get_recent_categories',
    'params': ['steemit', 10]
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'get_recovery_request',
    'params': ['steemit']
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'get_replies_by_last_update',
    'params': []
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'get_state',
    'params': []
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'get_transaction',
    'params': []
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'get_trending_categories',
    'params': []
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'get_trending_tags',
    'params': ['steemit', 10]
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'get_witness_by_account',
    'params': ['smooth.witness']
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'get_witness_count',
    'params': []
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'get_witness_schedule',
    'params': []
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'lookup_account_names',
    'params': ['steemit']
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'lookup_accounts',
    'params': ['steemit', 10]
}, {
    'id': 1,
    'jsonrpc': '2.0',
    'method': 'lookup_witness_accounts',
    'params': ['steemit', 10]
}]


@pytest.yield_fixture
def app():
    args = jussi.serve.parse_args()
    # run app
    app = Sanic('testApp')
    app.config.args = args
    app = jussi.logging_config.setup_logging(app)
    app = jussi.serve.setup_routes(app)
    app = jussi.middlewares.setup_middlewares(app)
    app = jussi.errors.setup_error_handlers(app)
    app = jussi.listeners.setup_listeners(app)
    yield app


@pytest.fixture(
    scope='function',
    params=['/', '/health/', '/.well-known/healthcheck.json'])
def healthcheck_path(request):
    return request.param


@pytest.fixture
def jrpc_response_validator():
    return jsonschema.Draft4Validator(RESPONSE_SCHEMA)


@pytest.fixture
def jrpc_request_validator():
    return jsonschema.Draft4Validator(REQUEST_SCHEMA)


@pytest.fixture
def valid_single_jrpc_request():
    return {'id': 1, 'jsonrpc': '2.0', 'method': 'get_block', 'params': [1000]}


@pytest.fixture
def valid_batch_jrpc_request(valid_single_jrpc_request):
    return [valid_single_jrpc_request, valid_single_jrpc_request]


@pytest.fixture(params=INVALID_JRPC_REQUESTS)
def invalid_jrpc_requests(request):
    yield request.param


@pytest.fixture(params=STEEMD_JSON_RPC_CALLS)
def all_steemd_jrpc_calls(request):
    yield request.param


@pytest.fixture(scope='function')
def memory_cache():

    return SimpleMemoryCache()
