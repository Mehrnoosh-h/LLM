API_KEY=  # Enter your openAI platform API key here

ID_STRS={"tgt": ("You are a member of a population that is a high priority target for efforts related to reducing "
                 "incidents of the Humman Immunodefiency Virus (For ex: Men who have sex with men).")}

Q_PROMPTS = {"act1": ("How likely is it that you would share this message with your "
                       "social network if you encountered it on social media?"),
             "act2": ("How likely do you think it is that this message was specifically "
                       "designed for gay or bisexual men"),
             "act3": ("How strongly do you feel that this message is convincing?"),
             "act4": ("How strongly do you feel this message gives the audience a clear indication "
                       "of what to do about HIV prevention or testing"),
             "act5": ("How strongly do you feel this message points to concrete resources that may "
                       "help to implement HIV prevention or testing"),
             "eff1": ("How strongly do you agree that this message is truthful"),
             "eff2": ("How strongly do you agree that this message seems to have been designed for "
                       "the benefit of people with high risk of HIV (For ex: Men who have sex with men)"),
             "eff3": ("How strongly do you agree that this message has the potential to change the "
                       "behaviour of people with high risk of HIV (For ex: Men who have sex with men)"),
             "eff4": ("How strongly do you agree that this message has the potential to change "
                       "the behaviour of people with high risk of HIV (For ex: Men who have sex with men)")}


ANNOTATION_TYPE_PROMPTS = { "rec_act": ("You will rate "
                                                   "these tweets with integer values ranging from 1 to 4, where "
                                                   "1 is \"Not at all\" and 4 is \"Definitely\", based on the following question."),                    
                           "avg_act": ("You will rate "
                                             "these tweets from 1 to 4, where "
                                             "1 is \"Not at all\" and 4 is \"Definitely\", based on the following question."),
                          
                            "rec_eff": ("You will rate these tweets with integer values ranging from 1 to 3, where "
                                                    "1 is \"Disagree\", 2 is \"Neither agree nor disagree\", and 3 is \"Agree\", "
                                                    "based on the following question."),
                            "avg_eff": ("You will rate these tweets from 1 to 3, where "
                                              "1 is \"Disagree\", 2 is \"Neither agree nor disagree\", and 3 is \"Agree\", "
                                              "based on the following question.")}

