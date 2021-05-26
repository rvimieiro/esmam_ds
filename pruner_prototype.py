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
        ## implement print debugging ##
        self.current_rule = rule
        pruned_rule = Rule(self._dataset, self._comparison)

        while len(self.current_rule.antecedent) > 1:
            pruning_flag = False
            # set to True if pruned rule has better quality than original rule
            current_antecedent = self.current_rule.antecedent.copy() #!

            #for attr_idx in antecedent_idx:
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
                    pruning_flag = True
                    self.current_rule = pruned_rule

            if not pruning_flag:
                # the overall quality did not increase after pruning procedure
                # considering every current attribute
                break
                # end of pruning

        # sys.exit(0)
        return self.current_rule
