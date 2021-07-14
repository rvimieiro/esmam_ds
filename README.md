# EsmamDS
## Development-refactoring of ESMAM-DS algorithm.

The Exceptional Survival Model Ant-Miner Diverse Search (EsmamDS) is an
EMM framework that extends previous work to provide a set of more diverse subgroups,
where diversity is sought regarding the subgroup’s description, coverage and model exceptionality.
An instance of Exceptional Model Mining is defined by a model class over the targets and a quality
measure over the model. Subgroups are generated following a search strategy, and
then, for each subgroup under consideration, the model class is induced over only
the data related to the subgroup. The quality measure is finally employed to in-
dividually evaluate subgroups with regard to their model characteristics (against
a baseline model), and the most interesting ones are provided in a final set of
(exceptional) subgroups.