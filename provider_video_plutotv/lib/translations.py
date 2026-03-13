# pylama:ignore=E203,E221
"""
MIT License

Copyright (C) 2026 ROCKY4546
https://github.com/rocky4546

This file is part of Cabernet

Permission is hereby granted, free of charge, to any person obtaining a copy of this software
and associated documentation files (the "Software"), to deal in the Software without restriction,
including without limitation the rights to use, copy, modify, merge, publish, distribute,
sublicense, and/or sell copies of the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or
substantial portions of the Software.
"""

from lib.tvheadend.epg_category import groups
from lib.tvheadend.epg_category import tvh_genres

plutotv_boot = 'gfpMXf5BjIUYyNUMj8aEzspQj8pNjRkMjRlMksiM'
plutotv_channels = 'gfpMXf5BjIUKtsiNgbl7jbl+kbSFtbLKjZlEzslMtsiKj8aEzspQj8pNjRkIjNzCgbp7jNl+kbSFtbLKuNl+kbSFtbLitf5U0RMZyNtZXNrMu4WZyx7PgsnU54WG5wtKyRiMubSCybi7X6/3XN5='
plutotv_service = 'gfpMXf5BjIU6tZnPz6nPXNrIzZ76tqC6gxdFyZrEjslMgsp6gxrIjsrKt49P5qSGXZnFXxLCzxHFzfkQz62='
plutotv_categories = 'gfpMXf5BjIUKtsiNgbl7jbl+kbSFtbLKjZlEzslMtsiKj8aEzspQj8pNjRkIjNzCgbp7jNl3zxr8yRi/ts5='
plutotv_epg = 'gfpMXf5BjIUKtsiNgbl7jbl+kbSFtbLKjZlEzslMtsiKj8aEzspQj8pNjRkIjNzCgbp7jRp/ybrEgbS7XKUKzxdIzcCT1qt6gxdFyZrEqbpKusPUiZpCXZdMgbUFusPU'
plutotv_d125c = 'w8oeuqay28lMXZr3yqC8sRlMXZr3yrUMgbC7yRrM2YGe28lMXZr3yqC8sNlQyZlCX8i7y8p1txURyZLQkbpK2YGe28lMXZr3yqC8sN3Mzfa1zx7PtbUCzw2E2wiKzfi7kbMPtCU+zfpGsRi7zfi/ts5Ys4Ev0wWU2fl7yxkFkNUFtZ78sNUYgYS6yNSZgbz1gxdFtxL7XYSQXfp/yNSKvwiGyfrMyRpN2YoTw8+euqaxkbLKtn/ZyR2egqa/yYaSme+e2wWetZUI2x+egbJe0c+v2wWe2wWe2wa/tYa/2cMU2x+BwYWe2wWe2wWe2wWe2fl7yxkFXxLCtN7FsNUYgYS7yZdYyxro2cMepZdEXNhv2wWe2wWe2wWe2wWeXNrEtYS6yNSZgbz1yNiAjZp3zxdyXNrEtYSGyfr8gbS1yNiAjZS3ybhFyxURts2+vrCyiNrFkbiEtbn8sqWU29t3yfl7wYWe2wWe2wWe2wWe2f+euqahX8r7wYWe2wWe2wWe2wWe2xiItbdOmG+e2wWegbke06+v2wWe2wWe2waYXZr3gKEv'

plutotv_groups = {
    'Animals + Nature': groups['DOCUMENTARIES'],
    'Anime': groups['KIDS'],
    'Classic TV': groups['CLASSICS'],
    'Comedy': groups['COMEDY'],
    'Competition Reality': groups['SPORTS'],
    'Daytime + Game Shows': groups['LIFESTYLE'],
    'Drama': groups['MYSTERY'],
    'En Español': groups['SPANISH'],
    'Entertainment': groups['ENTERTAINMENT'],
    'History + Science': groups['DOCUMENTARIES'],
    'Home + Food': groups['LIFESTYLE'],
    'Kids': groups['KIDS'],
    'Local News': groups['NEWS'],
    'Movies': groups['MOVIES'],
    'Music Videos': groups['MUSIC'],
    'News + Opinion': groups['NEWS'],
    'Reality': groups['REALITY'],
    'Sci-Fi': groups['MYSTERY'],
    'Sports': groups['SPORTS'],
    'True Crime': groups['MYSTERY'],
    'Westerns': groups['WESTERNS']
}

plutotv_tv_genres = {
    "Action & Adventure": [tvh_genres['ADVENTURE']],
    "Anime": [tvh_genres['CARTOON']],
    "Children & Family": [tvh_genres['KIDS']],
    "Classics": [tvh_genres['MOVIE']],
    "Comedy": [tvh_genres['COMEDY']],
    "Crime": [tvh_genres['THRILLER']],
    "Dance": [tvh_genres['MUSIC']],
    "Documentaries": [tvh_genres['DOCUMENTARY']],
    "Documentary": [tvh_genres['DOCUMENTARY']],
    "Drama": [tvh_genres['MOVIE']],
    "Entertainment": [tvh_genres['GAME']],
    "Faith & Spirituality": [tvh_genres['RELIGION']],
    "Faith and Spirituality": [tvh_genres['RELIGION']],
    "Food & Cooking": [tvh_genres['COOKING']],
    "Game Show": [tvh_genres['GAME']],
    "Home & Lifestyle": [tvh_genres['CULTURE']],
    "Horror": [tvh_genres['SF']],
    "Independent": [tvh_genres['NEWS_MAGAZINE']],
    "Instructional & Educational": [tvh_genres['EDUCATIONAL']],
    "Music": [tvh_genres['MUSIC']],
    "Musical": [tvh_genres['MUSIC']],
    "Musicals": [tvh_genres['MUSIC']],
    "News & Information": [tvh_genres['NEWS']],
    "News and Information": [tvh_genres['NEWS']],
    "Paranormal": [tvh_genres['SF']],
    "Reality": [tvh_genres['GAME']],
    "Romance": [tvh_genres['ROMANCE']],
    "Sci-Fi & Fantasy": [tvh_genres['SF']],
    "Sports": [tvh_genres['SPORT']],
    "Talk Show": [tvh_genres['TALK_SHOW']],
    "Telenovela": [tvh_genres['LANGUAGES']],
    "Thriller": [tvh_genres['THRILLER']],
    "Thrillers": [tvh_genres['THRILLER']],
    "Variety Show": [tvh_genres['VARIETY']],
    "Western": [tvh_genres['ADVENTURE']],
    "No information available": None,
    "Other": None,
    "Gay & Lesbian": None
}
