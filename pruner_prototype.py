import copy
from rule import Rule


class Pruner:

    def __init__(self, dataset, terms_mgr, sg_comparison):
        self._terms_mgr = terms_mgr
        self._dataset = dataset
        self.current_rule = None
        self._comparison = sg_comparison

    def prune(self, rule):
        """Prune rule's antecedent while its quality measure does not decrease
        or rule's length is greater than one condition.
        At each iteration all conditions are tested for removal, being chosen 
        the one which promotes maximum overall quality improvement.
        """
        self.current_rule = rule

        # print("Pruning  ", self.current_rule.antecedent)

        pruned_rule = Rule(self._dataset, self._comparison)

        # if len(self.current_rule.antecedent) == 1:
        #     print("Cannot be pruned: one antecedent only.")

        pruning_iteration = 1
        while len(self.current_rule.antecedent) > 1:
            pruned_rule_has_better_quality = False
            current_antecedent = self.current_rule.antecedent.copy()

            # print("Pruning iteration {}:".format(pruning_iteration),
            #       current_antecedent)

            # for attr_idx in antecedent_idx:
            for attr in current_antecedent:
                # new pruned rule antecedent and cases
                pruned_rule.antecedent = current_antecedent.copy()
                # atribuir os antecedentes da regra criada fora do while
                pruned_rule.antecedent.pop(attr, None)
                pruned_rule.set_cases(
                    self._terms_mgr.get_cases(pruned_rule.antecedent)
                )
                pruned_rule.set_fitness()

                if pruned_rule.fitness >= self.current_rule.fitness:
                    pruned_rule_has_better_quality = True
                    self.current_rule = pruned_rule
                pruning_iteration += 1

            if not pruned_rule_has_better_quality:
                break

        # print("Pruned rule:", self.current_rule.antecedent)
        # input()

        return self.current_rule
