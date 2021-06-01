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
        print()
        print(50*'*')
        print()
        self.current_rule = rule
        print("Received for pruning:", self.current_rule.antecedent)
        print("\nOriginal fitness:", self.current_rule.fitness)
        print()

        pruned_rule = Rule(self._dataset, self._comparison)

        if len(self.current_rule.antecedent) == 1:
            print("Cannot be pruned: one antecedent only.")
            print()
        else:
            pruning_iteration = 1
            print("\tInitializing pruning procedure\n")

            while len(self.current_rule.antecedent) > 1:

                pruned_rule_has_better_quality = False
                current_antecedent = self.current_rule.antecedent.copy()

                print("\tIteration {}, pruning".format(pruning_iteration),
                      current_antecedent, '\n')

                temp = (self.current_rule.fitness, None)
                for attr in current_antecedent:

                    pruned_rule.antecedent = current_antecedent.copy()
                    pruned_rule.antecedent.pop(attr, None)
                    pruned_rule.set_cases(self._terms_mgr.get_cases(pruned_rule.antecedent))
                    pruned_rule.set_fitness()
                    print("\t\t>> Fitness without '{}':".format(attr), pruned_rule.fitness)

                    if pruned_rule.fitness >= temp[0]:
                        print("\n\t\t\tPruned rule maintains or improves quality.")
                        print("\n\t\t\tSetting '{}' attribute for removal".format(attr))
                        temp = (pruned_rule.fitness, attr)
                    else:
                        print("\n\t\t\tPruned rule decreases quality.")
                    print()

                if temp[1] is None:
                    print("\tPruning does not improve overall quality.\n")
                    break

                print("\t\t(!) Deleting {} from pruned rule's antecedent.".format(temp[1]))
                print()
                del self.current_rule.antecedent[temp[1]]

                pruning_iteration += 1

            ## rule treatment
            self.current_rule.set_cases(self._terms_mgr.get_cases(self.current_rule.antecedent))
            self.current_rule.set_fitness()

            print("\tEnd of pruning procedure, returning rule:\n")
            print("\t\t@ Antecedent:", self.current_rule.antecedent)
            print()
            print("\t\t@ Fitness:", self.current_rule.fitness)
            input()

        return self.current_rule
