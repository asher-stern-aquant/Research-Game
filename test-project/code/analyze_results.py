import os
import pandas as pd
import json
import utils


BASE_PATH = os.path.dirname(__file__)
customerid = '6619'
productTypeid = '1'
prefix = f'{customerid}_{productTypeid}_'


def from_str_to_list(x):
    x = x.translate({ord(i): None for i in "]'[ "})
    x = x.split(',')
    return x


def load_prob():
    with open('./tmp/'+prefix+'posterior_solution_given_observation_prob_dict.json') as json_file:
        p_s_given_o = json.load(json_file)

    with open('./tmp/'+prefix+'FILTERED_posterior_solution_given_observation_prob_dict.json') as json_file:
        p_s_given_o_filtered = json.load(json_file)
    return p_s_given_o, p_s_given_o_filtered


def load_stats():
    df = pd.read_excel(BASE_PATH + '/simulations/' + f'{prefix}stats.xlsx')
    df['sequence'] = df['sequence'].apply(from_str_to_list)
    df['actual_solutions'] = df['actual solutions'].apply(from_str_to_list)
    df['show_solutions'] = df['show solutions'].apply(from_str_to_list)
    df['hide_solutions'] = df['hide solutions'].apply(from_str_to_list)
    return df


def analyze_show_zero_stats(df_stats, p_s_given_o, p_s_given_o_filtered):
    df_stats = df_stats[df_stats['show percentage'] == 0]
    count = 1
    for line in df_stats.itertuples(index=False):
        if line[1] == '[]':
            continue
        print('sequence #', count)
        print(line)
        for solution in line.show_solutions:
            for obs in line.sequence:
                if obs[0] != '~' and obs != '0':
                    if obs in p_s_given_o_filtered:
                        if solution in p_s_given_o_filtered[obs]:
                            sorted_prob = {k: v for k, v in sorted(p_s_given_o_filtered[obs].items(), key=lambda item: item[1], reverse=True)}
                            print(solution, 'given ', obs, ' probability: ', p_s_given_o_filtered[obs][solution])
                        else:
                            print('solution ', obs, ' is filtered')
                    else:
                        print('observation ', obs, ' is filtered')
        count += 1


def find_difference_before_and_after_filter(p_s_given_o, p_s_given_o_filtered):
    observations_pre_filter = list(p_s_given_o.keys())
    observations_post_filter = list(p_s_given_o_filtered.keys())
    solutions_pre_filter = list(p_s_given_o[observations_post_filter[0]].keys())
    solutions_post_filter = list(p_s_given_o_filtered[observations_post_filter[0]].keys())
    obs_diff = sorted(list(set(observations_pre_filter) - set(observations_post_filter)))
    sol_diff = sorted(list(set(solutions_pre_filter) - set(solutions_post_filter)))
    print('removed observations: ', obs_diff)
    print('removed solutions: ', sol_diff)


def find_duplicates_in_data():
    expert_sequence_path = BASE_PATH + '/inputs/' + f'{prefix}expert_sequences_inputs.csv'
    maq_groups_path = BASE_PATH + '/inputs/' + f'{prefix}investigations_observations.csv'
    df_expert_sequences, all_observations = utils.upload_expert_sequences(expert_sequence_path, maq_groups_path)
    # take only solutions sequences
    df_expert_seq_show_sol = df_expert_sequences[df_expert_sequences['action'] == 'SHOW_SOLUTIONS']
    df_expert_seq_dont_show_sol = df_expert_sequences[df_expert_sequences['action'] == 'DONT_SHOW_SOLUTIONS']
    # df_expert_seq_ask = df_expert_sequences[df_expert_sequences['action'] == 'ASK_SPECIFIC_QUESTION']
    df_expert_seq_solutions = pd.concat([df_expert_seq_show_sol, df_expert_seq_dont_show_sol])

    dict_of_duplicates = {}
    list_of_answers = []
    for sequence in df_expert_seq_solutions.itertuples(index=False):
        answers = set(sequence.observations_answer.split(','))
        if answers not in list_of_answers:
            list_of_answers.append(answers)

    index = 0
    for answer in list_of_answers:
        for sequence in df_expert_seq_solutions.itertuples(index=False):
            sequence_answers = set(sequence.observations_answer.split(','))
            if sequence_answers == answer:
                if index in dict_of_duplicates:
                    dict_of_duplicates[index].append(sequence)
                else:
                    dict_of_duplicates[index] = []
                    dict_of_duplicates[index].append(sequence)
        if len(dict_of_duplicates[index]) == 1:
            del dict_of_duplicates[index]
        index += 1

    number_of_duplicates = 0
    for key in dict_of_duplicates:
        number_of_duplicates += len(dict_of_duplicates[key])



p_s_given_o, p_s_given_o_filtered = load_prob()
#find_difference_before_and_after_filter(p_s_given_o, p_s_given_o_filtered)
stats = load_stats()
analyze_show_zero_stats(stats, p_s_given_o, p_s_given_o_filtered)