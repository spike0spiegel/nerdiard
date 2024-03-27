import pandas as pd

#STATS#
def calculate_player_accuracy(player_id):
    df = pd.read_csv(data)

    player_df = df[df['player_id'] == int(player_id)]
    player_df_ch = df[(df['player_id'] == int(player_id)) & (df['shot_type'] == 'Ч')]
    player_df_sv = df[(df['player_id'] == int(player_id)) & (df['shot_type'] == 'С')]

    non_zero_score_shots = player_df[player_df['shot_score'] != 0]['shot_score'].count()
    total_shots = player_df['shot_score'].count()
    accuracy = str(100 * non_zero_score_shots / total_shots)[:4] + '%'

    non_zero_score_shots_ch = player_df_ch[player_df_ch['shot_score'] != 0]['shot_score'].count()
    total_shots_ch = player_df_ch['shot_score'].count()
    accuracy_ch = str(100 * non_zero_score_shots_ch / total_shots_ch)[:4] + '%'


    non_zero_score_shots_sv = player_df_sv[player_df_sv['shot_score'] != 0]['shot_score'].count()
    total_shots_sv = player_df_sv['shot_score'].count()
    accuracy_sv = str(100 * non_zero_score_shots_sv / total_shots_sv)[:4] + '%'

    ch = str(100 * total_shots_ch / total_shots)[:4] + '%'
    sv = str(100 * total_shots_sv / total_shots)[:4] + '%'

    return {'accuracy': accuracy, 'ch': ch, 'sv': sv, 'accuracy_ch': accuracy_ch, 'accuracy_sv': accuracy_sv}