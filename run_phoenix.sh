set -ex

pushd phoenix

git switch adn
git pull
cargo make 
cd experimental/mrpc
cargo make
cd ../..

popd 

set +ex