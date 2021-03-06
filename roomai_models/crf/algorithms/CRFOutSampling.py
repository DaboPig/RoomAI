import roomai.common

class CRFOutSampling(object):

    def dfs(self, env, player, p0, p1, action=None, deep=0):

        if deep == 0:
            infos, public_state, person_states, private_state = env.init(
                {"backward_enable": True, "param_num_normal_players": 2})
        else:
            infos, public_state, person_states, private_state = env.forward(action)

        if public_state.is_terminal == True:
            turn = public_state.turn
            scores = public_state.scores
            result = scores[turn]

        else:

            turn = public_state.turn
            state = player.gen_state_feat(infos[turn])
            available_actions = infos[turn].person_state.available_actions.values()
            num_available_actions = len(available_actions)
            regrets = player.get_immediate_regrets(state, available_actions)
            strategies = player.get_averge_strategies(state, available_actions)

            cur_p = p0
            if turn == 1:   cur_p = p1
            opp_p = p1
            if turn == 1:   opp_p = p0

            cur_strategy = [0 for i in range(num_available_actions)]
            sum1 = 0
            for i in range(num_available_actions):
                sum1 += max(0, regrets[i])
            for i in range(num_available_actions):
                if sum1 > 0:
                    cur_strategy[i] = max(0, regrets[i]) / sum1
                else:
                    cur_strategy[i] = 1.0 / num_available_actions

            counterfactual_h_a = [0 for i in range(num_available_actions)]
            counterfactual_h = 0

            for i in range(num_available_actions):
                if turn == 0:
                    counterfactual_h_a[i] = -1 * self.dfs(env, player, p0 * cur_strategy[i], p1, available_actions[i],
                                                          deep + 1)
                else:
                    counterfactual_h_a[i] = -1 * self.dfs(env, player, p0, p1 * cur_strategy[i], available_actions[i],
                                                          deep + 1)

                counterfactual_h += cur_strategy[i] * counterfactual_h_a[i]

            new_regrets = [0 for i in range(num_available_actions)]
            new_strategies = [0 for i in range(num_available_actions)]
            for i in range(num_available_actions):
                new_regrets[i] = regrets[i] + opp_p * (counterfactual_h_a[i] - counterfactual_h)
                new_strategies[i] = strategies[i] + cur_p * cur_strategy[i]
                # new_strategies[i] =   cur_strategy[i]
                '''if state == "2_checkbet" and i == 1:
                    print player.strategies
                    print player.get_strategies(state,available_actions)
                    print strategies,new_strategies,cur_p,cur_strategy
                    '''

            player.update_immediate_regrets(state, available_actions, new_regrets)
            player.update_averge_strategies(state, available_actions, new_strategies)
            result = counterfactual_h

        if deep != 0:
            env.backward()
        return result





