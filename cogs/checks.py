from cogs.utils import get_config

class checkFuncs():
    def handleFlags(ctx, flags) -> bool:
        validFlags = [
            "alwaysTrue",
            "alwaysFalse"
        ] # More may be added
        debug = flags[0] == "debug"
        firstLoopIteration = True
        for flag in flags:
            if flag not in validFlags and flag != "debug":
                return f"'{flag}'"
            if debug and firstLoopIteration:
                firstLoopIteration = False
                continue
            elif debug:
                if flag == "alwaysTrue": return True
                elif flag == "alwaysFalse": return False
        return False

    def handleRoles(ctx, roles) -> bool:
        for roleID in roles:
            role = ctx.guild.get_role(roleID)
            if role in ctx.author.roles: return True
        return False

    def handleUsers(ctx, users) -> bool:
        if ctx.author.id in users:
            return True
        return False
    
    @classmethod
    def parseCheck(cls, ctx, data) -> bool:
        f, r, u = False, False, False
        if data['flags'] != []:
            f = cls.handleFlags(ctx, data['flags'])
            if type(f) != bool:
                print(f"Invalid flag defined: {f}")
                return False
        if data['roles'] != []:
            r = cls.handleRoles(ctx, data['roles'])
        if data['users'] != []:
            u = cls.handleUsers(ctx, data['users'])
        if True in [f, r, u]: return True
        return False

# Must be async because @commands.check() parses coro
async def check(ctx, check):
    return checkFuncs.parseCheck(ctx, check)