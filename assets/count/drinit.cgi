#┌─────────────────────────────────
#│ DREAM COUNTER v3.3 設定ファイル (2002/08/02)
#│ Copyright(C) Kent Web 2002
#│ webmaster@kent-web.com
#│ http://www.kent-web.com/
#└─────────────────────────────────

#------------#
#  基本設定  #
#------------#

# 管理パスワード（英数字で指定）
$pass = 'potbcycs';

# IPアドレスのチェック (0=no 1=yes) 
#   → yesの場合連続したIPアドレスはカウントアップしない
$ip_chk = 0;

# ログの自動生成 (0=no 1=yes)
$id_creat = 0;

# ログを置くサーバディレクトリ
#   → 現行ディレクトリであればこのままでよい
#   → 最後は必ず / で閉じる
#   → フルパスなら / から始める（http://からではない）
$datadir = './data/';

# rename関数によるログ更新 (0=no 1=yes)
#   → yes にするとログ破損が起きにくくなります
$rename = 1;

# ファイルロック機構
#   0 : しない
#   1 : する (symlink関数式)
#   2 : する (mkdir関数式)
$lockkey = 1;

# ロックファイルのサーバディレクトリ
#   → 最後は必ず / で閉じる
#   → フルパスなら / から始める（http://からではない）
$lockdir = './lock/';

# 他サイトからアクセスを排除
#   → 排除する   : dream.cgiを設置するURLを http://から記述
#   → 排除しない : 何も記述しない（このまま）
#   注：ただし「排除する」とした場合、設置するサーバや利用者のブラウザ
#       によっては自サイトからでもアクセスを排除する場合があります。
$base_url = "";

# 画像のあるデフォルト（初期値）のディレクトリ指定
#   → フルパスなら / から始める（http://からではない）
#   → 最後は必ず / で閉じる
$gifdir = './gif1/';

# 桁数指定の最大値（セキュリティ対策）
#   → これを超える桁数は指定しても無視されます。
$maxfig = 12;

# 本体のスクリプト名（初期値 dream.cgi)
$dream = './count.cgi';

#------------#
#  設定完了  #
#------------#

#----------------#
#  デコード処理  #
#----------------#
sub decode {
	local($buf, $key, $val);
	$postflag=0;
	if ($ENV{'REQUEST_METHOD'} eq "POST") {
		$postflag=1;
		read(STDIN, $buf, $ENV{'CONTENT_LENGTH'});
	} else { $buf = $ENV{'QUERY_STRING'}; }
	foreach (split(/&/, $buf)) {
		($key, $val) = split(/=/);
		$val =~ tr/+/ /;
		$val =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;

		$val =~ s/&/&amp;/g;
		$val =~ s/"/&quot;/g;
		$val =~ s/</&lt;/g;
		$val =~ s/>/&gt;/g;
		$val =~ s/\0//g;

		$in{$key} = $val;
	}
	$mode = $in{'mode'};
	if ($buf) { return (1); } else { return (0); }
}

#------------------#
#  HTMLのヘッダー  #
#------------------#
sub header {
	print "Content-type: text/html\n\n";
	print <<"EOM";
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html lang="ja">
<head>
<META HTTP-EQUIV="Content-type" CONTENT="text/html; charset=Shift_JIS">
<title>夢カウンタ</title></head>
<body>
EOM
}

#--------------#
#  ロック処理  #
#--------------#
sub lock {
	local($retry)=5;
	if (-e $lockfile) {
		local($mtime) = (stat($lockfile))[9];
		if ($mtime && $mtime < time - 60) { &unlock; }
	}
	# symlink関数式ロック
	if ($lockkey == 1) {
		while (!symlink(".", $lockfile)) {
			if (--$retry <= 0) { &error; }
			sleep(1);
		}
	# mkdir関数式ロック
	} elsif ($lockkey == 2) {
		while (!mkdir($lockfile, 0755)) {
			if (--$retry <= 0) { &error; }
			sleep(1);
		}
	}
	$lockflag=1;
}

#--------------#
#  ロック解除  #
#--------------#
sub unlock {
	if ($lockkey == 1) { unlink($lockfile); }
	elsif ($lockkey == 2) { rmdir($lockfile); }
	$lockflag=0;
}

#--------------------------#
#  データディレクトリ検索  #
#--------------------------#
sub datadir {
	local($dir, @dir, @file);

	## データディレクトリ読込
	# (1) opendir関数
	if (!opendir(DIR,"$datadir")) {
		@dir = readdir(DIR);
		closedir(DIR);
	}
	# (2) chdir関数
	else {
		$dir = $ENV{'SCRIPT_FILENAME'};
		$dir =~ s/[^\\\/]*$//;
		chdir($datadir) || &error("Dir Error : $datadir");
		@dir = <*>;
		if ($dir[0] eq '') {
			$ls = `ls`;
			@dir = split(/\s+/, $ls);

		}
		chdir($dir);
	}
	# ログチェック
	@file=();
	foreach (@dir) {
		if ($_ =~ /.+\.dat$/) { push(@file,$_); }
	}
	return (@file);
}

1;

