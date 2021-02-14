import pandas as pd
def load_and_prefilter(filepaths, options_dict):
    df = pd.read_csv(f'{filepaths[0]}')

    if options_dict['prefilter_items']:  # Оставим только 5000 самых популярных товаров
        popularity = df.groupby('item_id')['quantity'].sum().reset_index()
        popularity.rename(columns={'quantity': 'n_sold'}, inplace=True)
        top_5000 = popularity.sort_values('n_sold', ascending=False).head(5000).item_id.tolist()
        df.loc[~df['item_id'].isin(top_5000), 'item_id'] = 999999

    if options_dict['no_popular']:  # Уберем самые популярные
        popularity = df.groupby('item_id')['quantity'].sum().reset_index()
        popularity.rename(columns={'quantity': 'n_sold'}, inplace=True)
        top_n = popularity.sort_values('n_sold', ascending=False).head(options_dict['num_popular']).item_id.tolist()
        df.loc[df['item_id'].isin(top_n), 'item_id'] = 999998

    if options_dict['no_unpopular']:  # Уберем самые популярные
        popularity = df.groupby('item_id')['quantity'].sum().reset_index()
        popularity.rename(columns={'quantity': 'n_sold'}, inplace=True)
        top_n = popularity.sort_values('n_sold', ascending=True).head(options_dict['num_unpopular']).item_id.tolist()
        df.loc[df['item_id'].isin(top_n), 'item_id'] = 999997

    if options_dict['no_last_sales']:  # Уберем товары, которые не продавались за последнее время
        weeks = options_dict['months_last_sales'] * 4
        actual_time_data_frame = df[df['week_no'] >= df['week_no'].max() - weeks]
        old_time_data_frame = df[df['week_no'] < df['week_no'].max() - weeks]
        old_items = old_time_data_frame['item_id'].to_list()
        actual_items = actual_time_data_frame['item_id'].to_list()
        res = list(set(old_items) - set(actual_items))
        df.loc[df['item_id'].isin(res), 'item_id'] = 999996

    if options_dict['not_interesting_departments']:  # Уберем неинтересные для рекоммендаций категории (department)
        df_prods = pd.read_csv(f'{filepaths[1]}')
        filtered_by_departments = []
        for department in options_dict['filtered_departments']:
            filtered_by_departments += df_prods.loc[df_prods['DEPARTMENT'] == department]['PRODUCT_ID'].to_list()
        df.loc[df['item_id'].isin(filtered_by_departments), 'item_id'] = 999995

    if options_dict['no_profit_goods']:  # Уберем слишком дешёвые товары (на них не заработаем)
        price_df = df.groupby('item_id')['quantity', 'sales_value'].sum().reset_index()
        price_df['item_price'] = price_df['sales_value'] / price_df['quantity']
        low_price = price_df.describe()['item_price'][4]
        filtered_by_low_price = list(price_df.loc[price_df['item_price'] < low_price]['item_id'].unique())
        df.loc[df['item_id'].isin(filtered_by_low_price), 'item_id'] = 999994

    if options_dict['no_expensive_goods']:  # Уберем слишком дорогие товары.
        price_df = df.groupby('item_id')['quantity', 'sales_value'].sum().reset_index()
        price_df['item_price'] = price_df['sales_value'] / price_df['quantity']
        high_price = price_df.describe()['item_price'][6]
        filtered_by_low_price = list(price_df.loc[price_df['item_price'] > high_price]['item_id'].unique())
        df.loc[df['item_id'].isin(filtered_by_low_price), 'item_id'] = 999993

    return df

def postfilter_items():
    pass