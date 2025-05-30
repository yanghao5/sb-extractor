import warnings

# internal pkg
from core.validator import email
from core.validator import name
from core.validator import token

# third-party pkg
import toml

# validate cloudflare
def check_cloudflare(cloudflare):
    required_fields = ["CLOUDFLARE_ACCOUNT_ID", "CLOUDFLARE_API_KEY", "CLOUDFLARE_EMAIL", "CLOUDFLARE_KV_NAMESPACE_ID", "SUBSCRIBE_USER_TOKEN"]
    for field in required_fields:
        field_value=cloudflare.get(field,None)
        if field_value is None:
            raise ValueError(f"{field} in [cloudflare] is required, and don't be empty")
        
    # validate mail address
    try:
        mail = cloudflare.get("CLOUDFLARE_EMAIL")
        email.validate(mail)
    except AttributeError as e:
        raise ValueError(f"Invalid email format in [cloudflare] field: {mail}") from e
    
    # Check SUBSCRIBE_USER_TOKEN
    subscribe_user_token = cloudflare.get("SUBSCRIBE_USER_TOKEN")
    if not isinstance(subscribe_user_token, list):
        raise ValueError(
            "SUBSCRIBE_USER_TOKEN in [cloudflare] field must be a list."
        )
    if not subscribe_user_token: # Checks if list is empty
        raise ValueError(
            "SUBSCRIBE_USER_TOKEN in [cloudflare] field cannot be empty."
        )
    for t in subscribe_user_token:
        if not token.validate(t):
            raise ValueError(
                f"SUBSCRIBE_USER_TOKEN in [cloudflare] field haves invalid token {t}."
            )
            
# validate subscribes
def check_subscribes(subscribe_list):
    tags=[]
    for index,subscribe in enumerate(subscribe_list):
        url=subscribe.get("url",None)
        if not url:
            raise ValueError(f'providers.toml {index} [[subscribe]] field "url" is required and cannot be empty.')
        else:
            pass
        
        tag=subscribe.get("tag",None)
        if not tag: # This handles both None and ""
            raise ValueError(f'providers.toml {index} [[subscribe]] field "tag" is required and cannot be empty.')
        else:
            if tag in tags:
                raise ValueError(f"providers.toml {index} [[subscribe]] have duplicate tag {tag}")
            if name.validate(tag):
                tags.append(tag)
            else:
                raise ValueError(f"providers.toml {index} [[subscribe]] have invalid tag {tag}")
                
        # prefix
        prefix=subscribe.get("prefix",None)
        if not prefix:
            warnings.warn(f'providers.toml {index} [[subscribe]] prefix field is empty', DeprecationWarning)

        # exclude_keywords
        exclude_keywords=subscribe.get("exclude_keywords",None)
        if not exclude_keywords:
            warnings.warn(f'providers.toml {index} [[subscribe]] exclude_keywords field is empty', DeprecationWarning)
            
        # exclude_protocol
        exclude_protocol=subscribe.get("exclude_protocol",None)
        if not exclude_protocol:
            warnings.warn(f'providers.toml {index} [[subscribe]] exclude_protocol field is empty', DeprecationWarning)
        
# validate sort
def check_sorts(sort_list):
    for index,sort in enumerate(sort_list):
        # range
        _range=sort.get("range",None)
        if _range is None:
            raise ValueError(f'providers.toml {index} [[sort]] lack range field')
        if _range=="":
            raise ValueError(f'providers.toml {index} [[sort]] range field is empty')
        
         # mixed
        #mixed=sort.get("mixed","hello")
        # if mixed is None:
        #     raise ValueError(f'providers.toml {index} [[sort]] lack mixed field')
        # if mixed=="":
        #     raise ValueError(f'providers.toml {index} [[sort]] range mixed is empty')
        
        # keywords
        keywords=sort.get("keywords",None)
        if keywords is None:
            raise ValueError(f'providers.toml {index} [[sort]] lack keywords field')
        if not isinstance(keywords, list): # Ensure it's a list before checking length
            raise ValueError(f'providers.toml [[sort]] index {index} "keywords" field must be a list.')
        if len(keywords)<2:
            raise ValueError(f'providers.toml {index} [[sort]] keywords field must contain at least two keywords.')
        
            

# validate providers.toml
def validate(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = toml.load(f)
        
        # validate mode field
        mode = data.get("mode")
        if not (isinstance(mode, str) and mode in ["full", "tmpl", "nodes"]):
            raise ValueError('providers.toml mode field is required and must be one of ["full", "tmpl", "nodes"]')
        
        # validate tmpl_path field
        tmpl_path=data.get("tmpl_path",None)    
        if tmpl_path is None:
            raise ValueError('providers.toml tmpl_path field is required')
        else:
            pass
        
        # validate config_save_path field
        config_save_path=data.get("config_save_path",None)
        if config_save_path is None:
            raise ValueError('providers.toml config_save_path field is required')
        else:
            pass

        # validate nodes_save_path field
        nodes_save_path=data.get("nodes_save_path",None)
        if nodes_save_path is None:
            raise ValueError('providers.toml nodes_save_path field is required')
        
        # # validate [cloudflare] field
        cloudflare=data.get("cloudflare",None)
        if cloudflare is None:
            warnings.warn("providers.toml lack [cloudflare]", DeprecationWarning)
        else:
            check_cloudflare(cloudflare)

        # 校验 Subscribe
        subscribes=data.get("subscribe",None)
        if subscribes is None:
            raise ValueError('providers.toml [[subscribe]] field is required')
        else:
            check_subscribes(subscribes)

        # 校验 Subscribe
        sorts=data.get("sort",None)
        if sorts is None:
            warnings.warn('providers.toml lack [[sort]]', DeprecationWarning)
        else:
            check_sorts(sorts)

        print("\033[34m providers.toml file verification passed! \033[0m\n")
    
    except ValueError as ve:
        print(f"\033[34m Verification Error: {ve} \033[0m")
    except Exception as e:
        print(f"\033[34m Other Error: {e} \033[0m")

# 调用示例
if __name__ == "__main__":
    validate("your_config.toml")
