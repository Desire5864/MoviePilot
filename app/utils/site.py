from lxml import etree

from app.utils.string import StringUtils


class SiteUtils:
    # 站点更名映射：新域名 -> 站点资源包中的注册键
    # 站点资源包（user.sites.v2.bin）按注册键匹配索引器与解析器，
    # 站点换域名后直接用新域名查询会匹配不到，这里统一归一。
    _SITE_DOMAIN_ALIASES = {
        # 高清杜比：uhddolby.com -> hddolby.com
        "uhddolby.com": "hddolby.com",
    }

    @classmethod
    def normalize_domain(cls, url_or_domain: str) -> str:
        """
        将站点地址/域名归一为站点资源包中的注册键。

        仅用于「URL -> 查询键」的场景（数据库查询、流控、统计、资源包匹配），
        不能用于实际请求地址，否则会把请求打到旧域名。
        """
        domain = StringUtils.get_url_domain(url_or_domain or "")
        if not domain:
            return ""
        return cls._SITE_DOMAIN_ALIASES.get(domain, domain)

    @classmethod
    def is_logged_in(cls, html_text: str) -> bool:
        """
        判断站点是否已经登陆
        :param html_text:
        :return:
        """
        html = etree.HTML(html_text)
        try:
            if not StringUtils.is_valid_html_element(html):
                return False
            # 存在明显的密码输入框，说明未登录
            if html.xpath("//input[@type='password']"):
                return False
            # 是否存在登出和用户面板等链接
            xpaths = [
                '//a[contains(@href, "logout")'
                ' or contains(@data-url, "logout")'
                ' or contains(@href, "mybonus") '
                ' or contains(@onclick, "logout")'
                ' or contains(@href, "usercp")'
                ' or contains(@lay-on, "logout")]',
                '//form[contains(@action, "logout")]',
                '//div[@class="user-info-side"]',
                '//a[@id="myitem"]'
            ]
            for xpath in xpaths:
                if html.xpath(xpath):
                    return True
            return False
        finally:
            if html is not None:
                del html

    @classmethod
    def is_checkin(cls, html_text: str) -> bool:
        """
        判断站点是否已经签到
        :return True已签到 False未签到
        """
        html = etree.HTML(html_text)
        try:
            if not StringUtils.is_valid_html_element(html):
                return False
            # 站点签到支持的识别XPATH
            xpaths = [
                '//a[@id="signed"]',
                '//a[contains(@href, "attendance")]',
                '//a[contains(text(), "签到")]',
                '//a/b[contains(text(), "签 到")]',
                '//span[@id="sign_in"]/a',
                '//a[contains(@href, "addbonus")]',
                '//input[@class="dt_button"][contains(@value, "打卡")]',
                '//a[contains(@href, "sign_in")]',
                '//a[contains(@onclick, "do_signin")]',
                '//a[@id="do-attendance"]',
                '//shark-icon-button[@href="attendance.php"]'
            ]
            for xpath in xpaths:
                if html.xpath(xpath):
                    return False
            return True
        finally:
            if html is not None:
                del html
