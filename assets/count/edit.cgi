#!/usr/bin/perl

#┌─────────────────────────────────
#│ DREAM COUNTER MANAGER v3.3 (2002/08/02)
#│ Copyright(C) Kent Web 2002
#│ webmaster@kent-web.com
#│ http://www.kent-web.com/
#└─────────────────────────────────
$ver= 'Dream Manager v3.3';
#┌─────────────────────────────────
#│ [注意事項]
#│ 1. このスクリプトはフリーソフトです。このスクリプトを使用した
#│    いかなる損害に対して作者は一切の責任を負いません。
#│ 2. 設置に関する質問はサポート掲示板にお願いいたします。
#│    直接メールによる質問は一切お受けいたしておりません。
#└─────────────────────────────────

# IIS対策
if ($ENV{'SERVER_SOFTWARE'} =~ /IIS/i) {
	local($chdir) = $0;
	$chdir =~ s/[^\\]*$//;
	chdir($chdir);
}

# 設定ファイル取込
require './drinit.cgi';

# スクリプト名
$script = './edit.cgi';

#----------------------- これより処理開始 -----------------------#
&decode;
&header;
if ($in{'pass'} eq '') {
	print <<"EOM";
<div align="center">
<h4>パスワードを入力して下さい</h4>
<form action="$script" method="POST">
<input type=password name=pass size=8>
<input type=submit value=' 認証 '></form></div>
<!-- 著作権表\示（削除改変禁止）-->
<br><br><br><div align="right">
Copyright (C) <a href='http://www.kent-web.com/'>Kent Web</a> 2002<br>
<b>$ver</b></div>
</body>
</html>
EOM
	exit;
}
# 認証
&error('パスワードが違います') if ($in{'pass'} ne $pass);

# ログチェック
@file = &datadir;

# 新規作成
if ($mode eq 'new' && $in{'id'}) {
	# 入力チェック
	if ($in{'id'} =~ /[^A-Za-z0-9]/) {
		&error("使用できる文字は英数字のみです");
	}
	if ($in{'count'} =~ /\D/) {
		&error("開始カウント数は数字のみで指定して下さい");
	}

	$flag=0;
	foreach (@file) {
		if ($_ eq "$in{'id'}\.dat") { $flag=1; last; }
	}
	if ($flag) { &error("$in{'id'} は既に存在するID名です"); }

	# 作成
	open(OUT,">$datadir$in{'id'}\.dat") || &error("Write Error : $in{'id'}\.dat");
	print OUT $in{'count'};
	close(OUT);
	chmod(0666, "$datadir$in{'id'}\.dat");

	unshift(@file,"$in{'id'}\.dat");
}
# ログメンテ画面
elsif ($mode eq 'mente' && $in{'id'}) {
	# ロック開始
	if ($lockkey) {
		$lockfile = "$lockdir$in{'id'}\.lock";
		&lock;
	}

	open(IN,"$datadir$in{'id'}\.dat") || &error("Open Error : $in{'id'}\.dat");
	local($log) = <IN>;
	close(IN);
	($count, $ip) = split(/:/, $log);

	# ロック解除
	&unlock if ($lockkey);

	print "<form action=\"$script\" method=POST>\n";
	print "<input type=hidden name=pass value=\"$in{'pass'}\">\n";
	print "<input type=hidden name=mode value=mente2>\n";
	print "<input type=hidden name=id value=\"$in{'id'}\">\n";
	print "ID名 : <b>$in{'id'}</b><br>\n";
	print "カウント数 : <input type=text name=count size=8 value=\"$count\"><br>\n";
	print "<input type=submit value='修正する'>\n";
	print "</body>\n</html>\n";
	exit;
}
# ログメンテ実行
elsif ($mode eq 'mente2' && $in{'id'}) {
	if ($in{'count'} =~ /\D/) {
		&error("開始カウント数は数字のみで指定して下さい");
	}
	# ロック開始
	if ($lockkey) {
		$lockfile = "$lockdir$in{'id'}\.lock";
		&lock;
	}

	open(IN,"$datadir$in{'id'}\.dat") || &error("Open Error : $in{'id'}\.dat");
	local($log) = <IN>;
	close(IN);

	($count, $ip) = split(/:/, $log);

	open(OUT,">$datadir$in{'id'}\.dat") || &error("Write Error : $in{'id'}\.dat");
	print OUT "$in{'count'}\:$ip";
	close(OUT);

	# ロック解除
	&unlock if ($lockkey);
}
# ログ削除
elsif ($mode eq 'del' && $in{'id'}) {
	# ロック開始
	if ($lockkey) {
		$lockfile = "$lockdir$in{'id'}\.lock";
		&lock;
	}

	unlink("$datadir$in{'id'}\.dat") || &error("Delete Error : $in{'id'}\.dat");
	@file = &datadir;

	# ロック解除
	&unlock if ($lockkey);
}

print <<"EOM";
<h3>管理画面</h3>
<form action="$script" method=POST>
<input type=hidden name=pass value="$in{'pass'}">
<input type=hidden name=mode value="new">
<hr><b>1. 新規ログ作成</b><br><br>
ログID名 <input type=text name=id size=12> (英数字でIDを指定)<br>
カウント開始数 <input type=text name=count size=8 value="0"><br>
<input type=submit value="新規作成"></form>
<form action="$script" method=POST>
<input type=hidden name=pass value="$in{'pass'}">
<hr><b>2. ログメンテ</b><br><br>
<input type=submit value="選択する">
<select name=mode>
<option value="mente">修正
<option value="del">削除</select>
<DL>
EOM

foreach (@file) {
	s/\.dat$//;
	print "<DT><input type=radio name=id value=\"$_\">$_\n";
}

# 著作権表示（削除改変禁止）
print "</DL>\n</form>\n<hr><div align=right>\n";
print "Copyright (C) <a href='http://www.kent-web.com/'>Kent Web</a> 2002<br>\n";
print "<b>$ver</b></div>\n</body>\n</html>\n";
exit;


#--------------#
#  エラー処理  #
#--------------#
sub error {
	&unlock if ($lockflag);
	print "<h3>ERROR !</h3>\n";
	print "<font color=red>$_[0]</font>\n";
	print "</body>\n</html>\n";
	exit;
}

__END__

